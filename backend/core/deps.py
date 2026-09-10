"""常用依赖项 —— 当前用户、角色检查"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import verify_token
from backend.database import get_db
from backend.errors import InvalidTokenError, PermissionDeniedError
from backend.models import User

# 告诉 FastAPI：token 从 Authorization: Bearer xxx 里取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """解析 token → 从数据库取出当前用户对象"""
    try:
        payload = verify_token(token)
    except Exception:
        raise InvalidTokenError("无效的凭证")

    user = await db.get(User, payload["sub"])
    if user is None:
        raise InvalidTokenError("用户不存在")
    return user


def require_role(required_role: str):
    """依赖工厂：要求特定角色才能访问

    用法：user: User = Depends(require_role("owner"))
    """

    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            raise PermissionDeniedError(f"需要 {required_role} 角色才能操作")
        return user

    return role_checker
