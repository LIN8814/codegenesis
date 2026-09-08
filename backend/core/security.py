"""安全模块 —— JWT 签发与验证"""

import datetime

import jwt

# 密钥（生产环境必须从 .env 读，后面优化）
SECRET_KEY = "codegenesis-dev-secret-key-2026-keep-private"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2


def create_access_token(user_id: str, role: str = "member") -> str:
    """签发 JWT"""
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """验证 JWT，返回 payload（签名错误/过期都会抛异常）"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])