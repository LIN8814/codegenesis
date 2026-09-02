"""CodeGenesis 后端入口 —— 项目管理 API（数据库版）"""

import asyncio
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import get_db, init_db
from backend.models import Project as ProjectModel
from backend.schemas import BatchGenerateRequest, Project, ProjectCreate
from backend.services.agent_service import LLMCodeGenAgent
from backend.services.cache import CacheService
from backend.services.llm import LLMClient
from backend.exceptions import register_exception_handlers

# 初始化 LLM 客户端和 Agent
llm_client = LLMClient()
code_gen_agent = LLMCodeGenAgent(llm_client)
cache_service = CacheService()

app = FastAPI(
    title="CodeGenesis",
    description="AI Agent 协作式软件开发平台",
    version="0.2.0",
)

register_exception_handlers(app)

# CORS: 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React 开发服务器
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import time
import logging


@app.middleware("http")
async def log_request(request: Request, call_next):
    """记录每个请求的处理耗时"""
    start = time.perf_counter()
    response = await call_next(request)  # 放行，调用真正的接口
    elapsed = (time.perf_counter() - start) * 1000
    print(f"[中间件]{request.method} {request.url.path} 耗时: {elapsed:.0f}ms")
    return response


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("codegenesis.middleware ")


@app.middleware("http")
async def log_request(request: Request, call_next):
    """记录每个请求的处理耗时"""
    start = time.perf_counter()
    response = await call_next(request)  # 放行，调用真正的接口
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} 耗时: {elapsed:.0f}ms")
    return response


@app.on_event("startup")
async def on_startup():
    """服务器启动时自动建表（没有才创建）"""
    await init_db()


# ========== 数据模型（已移到 schemas.py） ==========

# ========== CRUD 接口 ==========


@app.post("/projects", response_model=Project, status_code=201, tags=["项目管理"])
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """创建一个新项目，Agent 将根据需求生成代码"""
    project_id = str(uuid.uuid4())[:8]  # 生成8位随机ID
    new_project = ProjectModel(
        id=project_id,
        name=project.name,
        description=project.description,
        tech_stack=project.tech_stack,
    )
    db.add(new_project)  # 加入会话
    await db.commit()  # 提交（真正写入数据库）
    await db.refresh(new_project)  # 刷新，拿到数据库生成的 created_at
    return new_project


@app.get("/projects", response_model=list[Project], tags=["项目管理"])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """列出所有项目（最新在前）"""
    result = await db.execute(
        select(ProjectModel).order_by(ProjectModel.created_at.desc())
    )
    return result.scalars().all()


@app.get("/projects/{project_id}", response_model=Project, tags=["项目管理"])
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个项目详情"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@app.put("/projects/{project_id}", response_model=Project, tags=["项目管理"])
async def update_project(
    project_id: str, update: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """更新项目信息"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    project.name = update.name
    project.description = update.description
    project.tech_stack = update.tech_stack
    await db.commit()
    await db.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=204, tags=["项目管理"])
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """删除项目"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")
    await db.delete(project)
    await db.commit()


@app.post("/projects/{project_id}/generate", response_model=Project, tags=["AI生成"])
async def generate_code(project_id: str, db: AsyncSession = Depends(get_db)):
    """触发 Agent 为项目生成代码（带缓存：相同需求不重复调 AI）"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 1. 计算缓存 key（需求 + 技术栈 → 哈希）
    cache_key = cache_service.make_key(
        "generate", project.description, str(project.tech_stack)
    )

    # 2. 先查缓存
    cached_code = await cache_service.get(cache_key)
    if cached_code:
        project.generated_code = cached_code
        project.status = "completed"
        await db.commit()
        await db.refresh(project)
        return project

    # 3. 未命中：调用 AI 生成，写入缓存
    code = await code_gen_agent.generate_code(project.description, project.tech_stack)
    await cache_service.set(cache_key, code, ttl=3600)

    project.generated_code = code
    project.status = "completed"
    await db.commit()
    await db.refresh(project)
    return project


@app.post("/projects/batch-generate", tags=["AI生成"])
async def batch_generate(
    request: BatchGenerateRequest, db: AsyncSession = Depends(get_db)
):
    """并发为多个项目生成代码，全部完成后一起返回"""
    project_ids = request.project_ids

    # 逐个从数据库取出项目，顺便验证存在性
    projects = []
    for project_id in project_ids:
        project = await db.get(ProjectModel, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        projects.append(project)

    async def generate_one(project: ProjectModel):
        """为单个项目生成代码（内部函数）"""
        code = await code_gen_agent.generate_code(
            project.description, project.tech_stack
        )
        project.generated_code = code
        project.status = "completed"
        return project

    # 并发执行所有生成任务，一起等
    await asyncio.gather(*[generate_one(p) for p in projects])
    await db.commit()
    return {"completed": project_ids}
