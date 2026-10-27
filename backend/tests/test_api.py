"""接口测试：认证、项目 CRUD、统计

注意：认证上线后，所有 /projects 接口都要求登录，
不带 token 的请求应该得到 401，而不是 200/201。
"""

import pytest


class TestAuth:
    def test_login_success(self, client, test_user):
        """正确的用户名密码 → 签发 token"""
        response = client.post(
            "/auth/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """密码错误 → 401"""
        response = client.post(
            "/auth/token",
            data={"username": test_user["username"], "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_TOKEN"

    def test_me_without_token(self, client):
        """未登录访问 /auth/me → 401"""
        assert client.get("/auth/me").status_code == 401

    def test_me_with_token(self, client, test_user, auth_headers):
        """带 token 访问 /auth/me → 返回当前用户"""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["username"] == test_user["username"]

    def test_duplicate_register(self, client, test_user):
        """重复注册同一用户名 → 409"""
        response = client.post("/auth/register", json=test_user)
        assert response.status_code == 409
        assert response.json()["code"] == "USER_ALREADY_EXISTS"

    def test_member_cannot_list_users(self, client, auth_headers):
        """普通 member 角色访问 owner 接口 → 403"""
        response = client.get("/auth/users", headers=auth_headers)
        assert response.status_code == 403
        assert response.json()["code"] == "PERMISSION_DENIED"


class TestProjectsRequireAuth:
    def test_list_requires_login(self, client):
        """未登录不能查看项目列表 → 401"""
        assert client.get("/projects").status_code == 401

    def test_create_requires_login(self, client):
        """未登录不能创建项目 → 401"""
        response = client.post(
            "/projects",
            json={"name": "未登录项目", "tech_stack": ["python"]},
        )
        assert response.status_code == 401


class TestProjectsAPI:
    def test_root_not_found(self, client):
        """根路径不存在 → 404"""
        assert client.get("/").status_code == 404

    def test_create_project(self, client, auth_headers):
        """登录后创建项目 → 201"""
        response = client.post(
            "/projects",
            json={
                "name": "测试项目",
                "description": "测试用",
                "tech_stack": ["python"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "测试项目"
        assert body["status"] == "pending"

    def test_get_project_list(self, client, auth_headers):
        """登录后获取项目列表 → 200"""
        response = client.get("/projects", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_project_not_found(self, client, auth_headers):
        """不存在的项目 → 404"""
        response = client.get("/projects/not_exist", headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["code"] == "PROJECT_NOT_FOUND"

    def test_update_project(self, client, auth_headers):
        """更新项目信息 → 200"""
        created = client.post(
            "/projects",
            json={"name": "待更新项目", "tech_stack": ["python"]},
            headers=auth_headers,
        ).json()

        response = client.put(
            f"/projects/{created['id']}",
            json={
                "name": "更新后的项目",
                "description": "改过了",
                "tech_stack": ["python", "fastapi"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "更新后的项目"

    def test_delete_project(self, client, auth_headers):
        """删除存在的项目 → 204，再查 → 404"""
        created = client.post(
            "/projects",
            json={"name": "待删除项目", "tech_stack": ["python"]},
            headers=auth_headers,
        ).json()

        response = client.delete(f"/projects/{created['id']}", headers=auth_headers)
        assert response.status_code == 204

        response = client.get(f"/projects/{created['id']}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_project_not_found(self, client, auth_headers):
        """删除不存在的项目 → 404"""
        response = client.delete("/projects/not_exist", headers=auth_headers)
        assert response.status_code == 404

    def test_generate_project_not_found(self, client, auth_headers):
        """对不存在的项目触发生成 → 404（不会真的调用 LLM）"""
        response = client.post("/projects/not_exist/generate", headers=auth_headers)
        assert response.status_code == 404

    def test_batch_generate_project_not_found(self, client, auth_headers):
        """批量生成时有不存在的项目 → 404（不会真的调用 LLM）"""
        response = client.post(
            "/projects/batch-generate",
            json={"project_ids": ["not_exist"]},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestStats:
    def test_stats_available(self, client):
        """统计接口 → 返回四个固定字段"""
        response = client.get("/stats")
        assert response.status_code == 200
        body = response.json()
        assert {"total_projects", "completed", "pending", "success_rate"} <= set(body)


class TestGenerateWithMockedLLM:
    """用假的 LLM 和假缓存测试生成链路：不花钱、不等待、不依赖 Redis"""

    @pytest.fixture()
    def fake_dependencies(self, monkeypatch):
        from backend.routers import projects as projects_router

        calls = {"generate": 0}
        store = {}

        async def fake_generate(description, tech_stack):
            calls["generate"] += 1
            return "print('hello')"

        async def fake_get(key):
            return store.get(key)

        async def fake_set(key, value, ttl=3600):
            store[key] = value

        monkeypatch.setattr(
            projects_router.code_gen_agent, "generate_code", fake_generate
        )
        monkeypatch.setattr(projects_router.cache_service, "get", fake_get)
        monkeypatch.setattr(projects_router.cache_service, "set", fake_set)
        return calls

    def test_generate_second_call_hits_cache(
        self, client, auth_headers, fake_dependencies
    ):
        """同一需求第二次生成应命中缓存，不再调用 LLM"""
        created = client.post(
            "/projects",
            json={
                "name": "缓存命中测试",
                "description": "写一个 hello",
                "tech_stack": ["python"],
            },
            headers=auth_headers,
        ).json()

        first = client.post(f"/projects/{created['id']}/generate", headers=auth_headers)
        second = client.post(
            f"/projects/{created['id']}/generate", headers=auth_headers
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["generated_code"] == "print('hello')"
        assert second.json()["generated_code"] == "print('hello')"
        assert fake_dependencies["generate"] == 1

    def test_batch_generate(self, client, auth_headers, fake_dependencies):
        """批量生成：每个项目各调用一次 LLM，全部完成"""
        project_ids = []
        for index in range(2):
            created = client.post(
                "/projects",
                json={
                    "name": f"批量测试{index}",
                    "description": f"需求{index}",
                    "tech_stack": ["python"],
                },
                headers=auth_headers,
            ).json()
            project_ids.append(created["id"])

        response = client.post(
            "/projects/batch-generate",
            json={"project_ids": project_ids},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["completed"] == project_ids
        assert fake_dependencies["generate"] == 2
