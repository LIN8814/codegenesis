"""pytest 公共夹具

两个关键点：
1. 测试使用独立的临时 SQLite 数据库，绝不碰开发用的 codegenesis.db。
   DATABASE_URL 必须在导入 backend 之前设置，因为 backend.config 在导入时就会读取配置。
2. 所有 /projects 接口都需要登录，所以统一提供 auth_headers 夹具。
"""

import os
import tempfile
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# 每次测试会话用独立的临时库，避免上一次运行的数据干扰
TEST_DB_PATH = (
    Path(tempfile.gettempdir()) / f"codegenesis_test_{uuid.uuid4().hex[:8]}.db"
)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"

from backend.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """整个测试会话共用一个 TestClient（进入上下文会触发 startup 建表）"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def test_user(client):
    """注册一个测试用户，返回其账号信息"""
    suffix = uuid.uuid4().hex[:8]
    user = {
        "username": f"testuser_{suffix}",
        "email": f"testuser_{suffix}@example.com",
        "password": "testpassword123",
    }
    response = client.post("/auth/register", json=user)
    assert response.status_code == 201, response.text
    return user


@pytest.fixture(scope="session")
def auth_headers(client, test_user):
    """登录测试用户，返回可直接放进请求头的 Bearer 认证信息"""
    response = client.post(
        "/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    """测试结束后删除临时数据库（Windows 上文件可能仍被连接占用，删不掉就跳过）"""
    yield
    try:
        TEST_DB_PATH.unlink(missing_ok=True)
    except OSError:
        pass
