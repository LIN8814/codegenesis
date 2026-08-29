"""Day 19 练习：串行 vs 并行调用 LLM"""

import asyncio
import time


async def fake_llm_call(task_name: str, delay: float = 2.0) -> str:
    """模拟一次 LLM API 调用（实际就是网络等待）"""
    print(f"  开始处理: {task_name}")
    await asyncio.sleep(delay)  # 模拟等待网络响应
    print(f"  完成处理: {task_name}")
    return f"result of {task_name}"


async def serial_demo(tasks: list[str]):
    """串行：一个一个来，总时间 = 所有任务时间相加"""
    results = []
    for task in tasks:
        results.append(await fake_llm_call(task))  # 等上一个做完才做下一个
    return results


async def parallel_demo(tasks: list[str]):
    """并行：同时发起，总时间 = 最慢的那个任务的时间"""
    return await asyncio.gather(*[fake_llm_call(t) for t in tasks])


async def main():
    tasks = ["需求A", "需求B", "需求C", "需求D", "需求E"]  # 5个任务，每个2秒

    print("=== 串行模式 ===")
    t0 = time.perf_counter()
    await serial_demo(tasks)
    print(f"串行耗时: {time.perf_counter() - t0:.2f}s\n")

    print("=== 并行模式 ===")
    t0 = time.perf_counter()
    await parallel_demo(tasks)
    print(f"并行耗时: {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
