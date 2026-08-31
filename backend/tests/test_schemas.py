"""Pydantic 模型验证器测试"""

import pytest
from backend.schemas import ProjectCreate


class TestProjectCreate:
    def test_valid_project(self):
        """正常数据能通过"""
        project = ProjectCreate(name="智能客服", tech_stack=["python", "fastapi"])
        assert project.name == "智能客服"

    def test_name_not_numeric(self):
        """名字全是数字 → 报错"""
        with pytest.raises(ValueError):
            ProjectCreate(name="12345")

    def test_name_strip_whitespace(self):
        """名字首尾空格被清理"""
        project = ProjectCreate(name="  智能客服  ")
        assert project.name == "智能客服"

    def test_tech_stack_dedup(self):
        """技术栈自动去重"""
        project = ProjectCreate(name="测试", tech_stack=["python", "python", "fastapi"])
        assert project.tech_stack == ["python", "fastapi"]

    def test_empty_tech_stack(self):
        """空技术栈 → 报错（min_length=1）"""
        with pytest.raises(ValueError):
            ProjectCreate(name="测试", tech_stack=[])

    def test_project_type_literal(self):
        """project_type 只能取合法值"""
        with pytest.raises(ValueError):
            ProjectCreate(name="测试", project_type="not_a_type")
