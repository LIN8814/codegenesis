"""CodeGenesis 后端入口 —— 只做组装(app 创建 + 路由注册 + 中间件)"""

import logging
import time


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.exceptions import register_exception_handlers
from backend.routers import projects, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("codegenesis.main")

app = FastAPI(
    title="CodeGenesis",
    description="AI Agent 协作式软件开发平台",
    version="0.2.0",
)

register_exception_handlers(app)

# CORS: 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React 开发服务器
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    """记录每个请求的处理耗时"""
    start = time.perf_counter()
    response = await call_next(request)  # 放行，调用真正的接口
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} 耗时: {elapsed:.0f}ms")
    return response


@app.on_event("startup")
async def on_startup():
    """服务器启动时自动建表（没有才创建）"""
    await init_db()


# 注册业务路由
app.include_router(projects.router)
app.include_router(stats.router)    