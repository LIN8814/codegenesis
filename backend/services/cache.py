"""Redis 缓存服务 —— 缓存 LLM 生成结果，省 token"""

import hashlib
import redis.asyncio as redis
from backend.config import settings


class CacheService:
    """基于 Redis 的缓存服务"""

    def __init__(self):
        # decode_responses=True: 返回的字节自动转成字符串
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    def make_key(self, prefix: str, *args) -> str:
        """生成缓存 key：把需求内容哈希成固定长度"""
        content = ":".join(str(a) for a in args)
        digest = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{prefix}:{digest}"

    async def get(self, key: str) -> str | None:
        """读缓存（没有返回 None）"""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """写缓存，默认 1 小时过期"""
        await self.redis.set(key, value, ex=ttl)
