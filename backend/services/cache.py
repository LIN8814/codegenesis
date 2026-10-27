"""Redis 缓存服务 —— 缓存 LLM 生成结果，省 token

缓存只是加速器，不是核心链路：Redis 连不上时按未命中处理，
继续调用 LLM，绝不能因为缓存故障让整个接口失败（fail-open）。
"""

import hashlib
import logging

import redis.asyncio as redis
from redis.exceptions import RedisError

from backend.config import settings

logger = logging.getLogger("codegenesis.cache")


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
        """读缓存（没有或读取失败都返回 None，按未命中处理）"""
        try:
            return await self.redis.get(key)
        except (RedisError, OSError) as exc:
            logger.warning("缓存读取失败，按未命中处理: %s", exc)
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """写缓存，默认 1 小时过期（写入失败只记日志，不影响主流程）"""
        try:
            await self.redis.set(key, value, ex=ttl)
        except (RedisError, OSError) as exc:
            logger.warning("缓存写入失败，已跳过: %s", exc)
