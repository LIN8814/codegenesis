"""Pydantic 数据模型 —— 请求/响应格式"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime


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
    def name_must_not_be_numeric(cls, v: str) -> str:
        """项目名称不能全是数字，并去掉首尾空格"""
        if v.isdigit():
            raise ValueError("项目名称不能是纯数字")
        return v.strip()

    @model_validator(mode="after")
    def validate_tech_stack(self):
        """tech_stack 去重保序"""
        self.tech_stack = list(dict.fromkeys(self.tech_stack))
        return self


class Project(BaseModel):
    """项目的完整表示（响应给前端）"""

    model_config = {"from_attributes": True}  # 允许从 ORM 对象直接转换

    id: str
    name: str
    description: str = ""
    tech_stack: list[str] = ["python"]
    status: str = "pending"
    created_at: datetime
    generated_code: Optional[str] = None


class BatchGenerateRequest(BaseModel):
    """批量生成请求体"""

    project_ids: list[str] = Field(..., min_length=1)
