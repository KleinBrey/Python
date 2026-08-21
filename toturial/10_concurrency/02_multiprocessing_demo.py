"""
==================================================
知识点：multiprocessing 多进程
==================================================

多进程使用独立 Python 解释器和内存，可利用多核执行 CPU 密集任务；
代价是启动与进程间传输更重。入口保护在 macOS/Windows 尤其重要。
"""

from concurrent.futures import ProcessPoolExecutor

def square(number: int) -> int:
    return number * number


def main() -> None:
    # 上下文退出时会等待并清理进程。map 保持输入顺序返回结果。
    numbers = [1, 2, 3, 4]
    try:
        with ProcessPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(square, numbers))
    except (OSError, PermissionError) as error:
        # 某些在线沙箱/受限容器禁止创建系统信号量或子进程。
        # 给出可理解的降级结果，让案例仍可单独运行；普通本地环境会走上面的进程池。
        print(f"当前环境不允许创建子进程，改用顺序演示：{type(error).__name__}")
        results = [square(number) for number in numbers]
    print(results)


if __name__ == "__main__":
    main()

# 传给子进程的函数/参数通常必须可序列化，函数应定义在模块顶层。
# 进程默认不共享普通全局变量；大量小任务可能因通信成本反而更慢。

"""
本节总结：CPU 密集可考虑多进程；必须使用入口保护；评估启动和通信开销。
"""
