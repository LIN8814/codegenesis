"""项目管理路由 —— 所有 /projects 接口"""

import asyncio
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Project as ProjectModel
from backend.schemas import BatchGenerateRequest, Project, ProjectCreate
from backend.errors import ProjectNotFoundError
from backend.services.agent_service import LLMCodeGenAgent
from backend.services.cache import CacheService
from backend.services.llm import LLMClient


# 创建路由对象：所有接口路径自动带 /projects 前缀，统一打标签
router = APIRouter(prefix="/projects", tags=["项目管理"])

# Agent 服务（从 main.py 挪过来）
llm_client = LLMClient()
code_gen_agent = LLMCodeGenAgent(llm_client)
cache_service = CacheService()


@router.post("", response_model=Project, status_code=201)
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


@router.get("", response_model=list[Project])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """列出所有项目（最新在前）"""
    result = await db.execute(
        select(ProjectModel).order_by(ProjectModel.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个项目详情"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("项目不存在")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str, update: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """更新项目信息"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("项目不存在")
    project.name = update.name
    project.description = update.description
    project.tech_stack = update.tech_stack
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """删除项目"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("项目不存在")
    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/generate", response_model=Project)
async def generate_code(project_id: str, db: AsyncSession = Depends(get_db)):
    """触发 Agent 为项目生成代码（带缓存：相同需求不重复调 AI）"""
    project = await db.get(ProjectModel, project_id)
    if project is None:
        raise ProjectNotFoundError("项目不存在")

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


@router.post("/batch-generate")
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
            raise ProjectNotFoundError(f"项目不存在: {project_id}")
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
