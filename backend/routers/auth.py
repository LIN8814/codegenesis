"""认证路由 —— 登录接口（周一会完善成完整版）"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.core.security import create_access_token, verify_token
from backend.errors import InvalidTokenError

router = APIRouter(prefix="/auth", tags=["认证"])

# 告诉 FastAPI：token 从 Authorization: Bearer xxx 里取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录：验证用户名密码 → 签发 JWT"""
    # ⚠️ 临时版：写死的账号（明天接真实 User 表）
    if form_data.username != "admin" or form_data.password != "admin123":
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user_id="admin", role="owner")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    """测试接口：带着 token 访问，返回你的身份"""
    try:
        payload = verify_token(token)
    except Exception:
        raise InvalidTokenError("无效的凭证")
    return {"user_id": payload["sub"], "role": payload["role"]}
