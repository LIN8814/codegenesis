"""CodeGenesis 后端入口 —— 项目管理 API"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

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
    tech_stack: list[str] = Field(default=["python"], description="技术栈")


class Project(ProjectCreate):
    """完整的项目对象（在 ProjectCreate 基础上多几个字段）"""

    id: str
    status: str = "pending"
    created_at: str
    generated_code: Optional[str] = None


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
