"""认证路由 —— 注册/登录/当前用户"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user, require_role
from backend.core.security import create_access_token, hash_password, verify_password
from backend.database import get_db
from backend.errors import InvalidTokenError, UserAlreadyExistsError
from backend.models import User
from backend.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["认证"])


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
async def get_me(current_user: User = Depends(get_current_user)):
    """返回当前登录用户的信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.get("/users")
async def list_users(
    current_user: User = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
):
    """列出所有用户（仅 owner 角色可访问）"""
    result = await db.execute(select(User))
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role}
        for u in result.scalars().all()
    ]


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
