"""缓存服务测试：Redis 故障时必须降级，不能拖垮主流程"""

import asyncio

from redis.exceptions import ConnectionError as RedisConnectionError

from backend.services.cache import CacheService


class BrokenRedis:
    """模拟 Redis 挂掉：所有命令都抛连接异常"""

    async def get(self, key):
        raise RedisConnectionError("redis is down")

    async def set(self, key, value, ex=None):
        raise RedisConnectionError("redis is down")


def test_make_key_is_stable_and_distinct():
    """同样的输入得到同样的 key，不同输入得到不同的 key"""
    service = CacheService()
    first = service.make_key("generate", "写一个 hello 接口", "['python']")
    second = service.make_key("generate", "写一个 hello 接口", "['python']")
    other = service.make_key("generate", "写一个 goodbye 接口", "['python']")

    assert first == second
    assert first != other
    assert first.startswith("generate:")


def test_get_returns_none_when_redis_down():
    """Redis 读失败 → 当作未命中，返回 None"""
    service = CacheService()
    service.redis = BrokenRedis()  # type: ignore[assignment]

    assert asyncio.run(service.get("generate:test")) is None


def test_set_does_not_raise_when_redis_down():
    """Redis 写失败 → 只记日志，不向上抛异常"""
    service = CacheService()
    service.redis = BrokenRedis()  # type: ignore[assignment]

    asyncio.run(service.set("generate:test", "生成的代码"))
