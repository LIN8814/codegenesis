"""用 Python 操作 Redis"""

import asyncio

import redis.asyncio as redis


async def main():
    # 连接 Redis（端口 6379，和 redis-cli 连的是同一个）
    r = redis.from_url("redis://localhost:6379", decode_responses=True)

    # 1. String + 过期时间
    await r.set("demo:user", "xiaoming", ex=60)
    print("GET demo:user →", await r.get("demo:user"))
    print("TTL demo:user →", await r.ttl("demo:user"), "秒后过期")

    # 2. List 任务队列
    await r.lpush("demo:queue", "任务1", "任务2", "任务3")
    print("RPOP →", await r.rpop("demo:queue"))
    print("RPOP →", await r.rpop("demo:queue"))
    print("队列长度 →", await r.llen("demo:queue"))

    # 3. 模拟缓存命中
    key = "cache:generate:abc123"
    await r.set(key, "这是缓存的代码", ex=3600)
    print("命中缓存 →", await r.get(key))

    # 4. 缓存未命中（key 不存在）
    print("未命中 →", await r.get("cache:generate:not_exist"))

    await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())
