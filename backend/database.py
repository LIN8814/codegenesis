"""数据库连接与初始化"""

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from backend.config import settings
from backend.models import Base

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,  # 从 config.py 读取（本地默认 SQLite）
    echo=settings.debug,  # 打印生成的 SQL（学习时开着很有用）
)

# 会话工厂：每次操作数据库从这里拿一个会话
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """启动时调用：创建所有表（没有才创建）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI 依赖：每个请求拿一个会话，用完自动关闭"""
    async with async_session() as session:
        yield session
