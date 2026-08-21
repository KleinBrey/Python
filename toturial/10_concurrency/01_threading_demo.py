"""
==================================================
知识点：Thread、start、join、daemon 与 Lock
==================================================
"""

import threading
import time

def download(name: str, delay: float) -> None:
    print(name, "开始")
    time.sleep(delay)
    print(name, "完成")


threads = [
    threading.Thread(target=download, args=("行情 A", 0.02), name="worker-a"),
    threading.Thread(target=download, args=("行情 B", 0.01), name="worker-b"),
]
for thread in threads:
    thread.start()  # 提交运行后顺序由调度器决定，不保证固定
for thread in threads:
    thread.join()   # 等待该线程结束，避免主线程提前退出

counter = 0
lock = threading.Lock()

def increment_many() -> None:
    global counter
    for _ in range(1000):
        # “读-改-写”共享状态需要锁保护；with 保证锁最终释放。
        with lock:
            counter += 1


workers = [threading.Thread(target=increment_many) for _ in range(3)]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()
print("安全计数：", counter)

# daemon=True 表示后台线程，不会阻止程序退出；不能依赖它完成重要写入。
daemon = threading.Thread(target=lambda: None, daemon=True)
daemon.start()
daemon.join()

"""
本节总结：start 启动，join 等待；线程顺序不确定；共享可变状态用 Lock。
"""
