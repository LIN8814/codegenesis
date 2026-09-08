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


from passlib.context import CryptContext

# bcrypt 哈希上下文（passlib 的配置对象）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """明文密码 → 哈希值（bcrypt 只用前 72 字节，按字节截断）"""
    encoded = password.encode("utf-8")[:72]
    return pwd_context.hash(encoded)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证：用户输入的明文密码 vs 数据库存的哈希"""
    encoded = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(encoded, hashed_password)