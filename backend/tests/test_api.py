"""API 接口测试（用 FastAPI TestClient，不需要真的起服务器）"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestProjectsAPI:
    def test_root_not_found(self):
        """根路径不存在 → 404"""
        response = client.get("/")
        assert response.status_code == 404

    def test_create_project(self):
        """创建项目 → 201"""
        response = client.post(
            "/projects",
            json={
                "name": "测试项目",
                "description": "测试用",
                "tech_stack": ["python"],
            },
        )
        assert response.status_code == 201
        assert response.json()["name"] == "测试项目"

    def test_get_project_list(self):
        """项目列表接口可访问"""
        response = client.get("/projects")
        assert response.status_code == 200

    def test_get_project_not_found(self):
        """不存在的项目 → 404"""
        response = client.get("/projects/not_exist")
        assert response.status_code == 404

    def test_delete_project(self):
        """删除不存在的项目 → 404"""
        response = client.delete("/projects/not_exist")
        assert response.status_code == 404
