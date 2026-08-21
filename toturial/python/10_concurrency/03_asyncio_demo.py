"""
==================================================
知识点：async def、await、asyncio.run 与 gather
==================================================
"""

import asyncio
from time import perf_counter

async def fetch_price(symbol: str, delay: float) -> dict[str, object]:
    # await 暂停当前协程，让事件循环运行其他就绪任务。
    # asyncio.sleep 模拟异步 I/O；不能换成 time.sleep，否则会阻塞事件循环。
    await asyncio.sleep(delay)
    return {"symbol": symbol, "price": 10.5}


async def main() -> None:
    start = perf_counter()
    results = await asyncio.gather(
        fetch_price("600519", 0.02),
        fetch_price("000001", 0.01),
    )
    print(results)
    print(f"异步并发约耗时：{perf_counter() - start:.3f} 秒")


if __name__ == "__main__":
    # asyncio.run 创建事件循环、运行顶层协程并完成清理，脚本入口最常用。
    asyncio.run(main())

# 调用 async def 只得到 coroutine，必须 await 或交给事件循环。
# asyncio 适合大量 I/O 等待，不会自动让 CPU 密集计算变快。

"""
练习：并发获取三个代码，每个延迟 0.01 秒并打印结果。

# ==========================
# 参考答案（放在 main 中）
# ==========================
# results = await asyncio.gather(*(fetch_price(code, 0.01) for code in codes))

本节总结：async def 定义协程；await 让出控制；gather 并发等待多个协程。
"""
