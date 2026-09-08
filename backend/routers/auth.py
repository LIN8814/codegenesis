"""认证路由 —— 注册/登录/当前用户"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)
from backend.database import get_db
from backend.errors import InvalidTokenError, UserAlreadyExistsError
from backend.models import User
from backend.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["认证"])

# 告诉 FastAPI：token 从 Authorization: Bearer xxx 里取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """登录：查用户表验证密码 → 签发 JWT"""
    # 1. 按用户名查用户
    user = await db.scalar(select(User).where(User.username == form_data.username))
    if user is None:
        raise InvalidTokenError("用户名或密码错误")

    # 2. 验证密码（哈希比对，不比对明文）
    if not verify_password(form_data.password, user.password_hash):
        raise InvalidTokenError("用户名或密码错误")

    # 3. 签发 token（用数据库里的真实用户 id 和 role）
    token = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    """测试接口：带着 token 访问，返回你的身份"""
    try:
        payload = verify_token(token)
    except Exception:
        raise InvalidTokenError("无效的凭证")
    return {"user_id": payload["sub"], "role": payload["role"]}


@router.post("/register", status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 1. 检查用户名/邮箱是否已存在
    existing = await db.scalar(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    if existing:
        raise UserAlreadyExistsError("用户名或邮箱已被注册")

    # 2. 创建用户（密码存哈希！绝不存明文）
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
