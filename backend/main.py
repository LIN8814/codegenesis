"""CodeGenesis 后端入口 —— 项目管理 API"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime
import uuid
import asyncio
from backend.services.llm import LLMClient
from backend.services.agent_service import LLMCodeGenAgent

# 初始化 LLM 客户端和 Agent
llm_client = LLMClient()
code_gen_agent = LLMCodeGenAgent(llm_client)

app = FastAPI(
    title="CodeGenesis",
    description="AI Agent 协作式软件开发平台",
    version="0.1.0",
)


# ========== 数据模型（Pydantic 定义数据结构） ==========


class ProjectCreate(BaseModel):
    """创建项目时客户端要提交的数据"""

    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: str = Field(default="", max_length=500, description="项目需求描述")
    tech_stack: list[str] = Field(
        default=["python"], min_length=1, description="技术栈"
    )
    project_type: Literal["web_app", "cli_tool", "api_service", "other"] = "web_app"

    @field_validator("name")
    @classmethod
    def name_must_not_be_numeric(cls, v: str) -> str:  # 装饰器：该函数负责校验NAME字段
        if v.isdigit():
            raise ValueError("项目名称不能是纯数字")
        return v.strip()

    @model_validator(mode="after")
    def validate_tech_stack(self):
        self.tech_stack = list(dict.fromkeys(self.tech_stack))  # 去重
        return self


class Project(ProjectCreate):
    """完整的项目对象（在 ProjectCreate 基础上多几个字段）"""

    id: str
    status: str = "pending"
    created_at: str
    generated_code: Optional[str] = None


class BatchGenerateRequest(BaseModel):
    """批量生成请求体"""

    project_ids: list[str] = Field(..., min_length=1)


# ========== 内存数据库（Phase 1 之前先不用真数据库） ==========

projects_db: dict[str, Project] = {}


# ========== CRUD 接口 ==========


@app.post("/projects", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate):
    """创建一个新项目，Agent 将根据需求生成代码"""
    project_id = str(uuid.uuid4())[:8]  # 生成8位随机ID
    new_project = Project(
        id=project_id,
        **project.model_dump(),
        created_at=datetime.now().isoformat(),
    )
    projects_db[project_id] = new_project  # 存进内存
    return new_project


@app.get("/projects", response_model=list[Project])
async def list_projects():
    """列出所有项目"""
    return list(projects_db.values())


@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """获取单个项目详情"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="项目不存在")
    return projects_db[project_id]


@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, update: ProjectCreate):
    """更新项目信息"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="项目不存在")
    project = projects_db[project_id]
    project.name = update.name
    project.description = update.description
    project.tech_stack = update.tech_stack
    return project


@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """删除项目"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="项目不存在")
    del projects_db[project_id]


@app.post("/projects/{project_id}/generate", response_model=Project)
async def generate_code(project_id: str):
    """触发 Agent 为项目生成代码"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="项目不存在")

    project = projects_db[project_id]
    code = await code_gen_agent.generate_code(project.description, project.tech_stack)
    project.generated_code = code
    project.status = "completed"

    return project


@app.post("/projects/batch-generate")
async def batch_generate(request: BatchGenerateRequest):
    """并发为多个项目生成代码，全部完成后一起返回"""
    project_ids = request.project_ids
    # 先检查所有 id 是否存在
    missing = [
        project_id for project_id in project_ids if project_id not in projects_db
    ]
    if missing:
        raise HTTPException(status_code=404, detail=f"项目不存在: {missing}")

    async def generate_one(project_id: str):
        """为单个项目生成代码（内部函数）"""
        project = projects_db[project_id]
        code = await code_gen_agent.generate_code(
            project.description, project.tech_stack
        )
        project.generated_code = code
        project.status = "completed"
        return project_id

    # 并发执行所有生成任务，一起等
    await asyncio.gather(*[generate_one(project_id) for project_id in project_ids])
    return {"completed": project_ids}
