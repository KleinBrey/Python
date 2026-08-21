"""
==================================================
知识点：os、sys 与 time
==================================================
"""

import os
import sys
import time
from pathlib import Path

print("Python 版本：", sys.version.split()[0])
print("命令行参数：", sys.argv)
print("当前工作目录：", Path.cwd())

# os.environ 读取环境变量。不要打印整个环境，它可能包含密码和令牌。
app_mode = os.environ.get("APP_MODE", "development")
print("运行模式：", app_mode)

# time.time() 是 Unix 时间戳；perf_counter() 更适合测量耗时。
timestamp = time.time()
start = time.perf_counter()
sum(range(100_000))
elapsed = time.perf_counter() - start
print("时间戳：", timestamp)
print(f"计算耗时：{elapsed:.6f} 秒")

# time.sleep 会阻塞当前线程。这里只解释，不实际等待，避免教学脚本变慢。
# time.sleep(1)

"""
本节总结：sys 提供解释器信息，os 提供系统接口，perf_counter 用于测耗时。
"""
