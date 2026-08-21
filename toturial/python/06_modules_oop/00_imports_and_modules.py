"""
==================================================
知识点：模块、import、标准库与入口保护
==================================================

一个 .py 文件就是一个模块；含 __init__.py 的目录通常是一个普通包。
"""

import math
from datetime import datetime
from pathlib import Path as FilePath  # as 可解决重名或提供公认简称

print(math.sqrt(16))
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(FilePath(__file__).name)

# Python 大致按以下位置查找模块：
# 1. 当前脚本所在目录；2. PYTHONPATH；3. 标准库；4. site-packages 第三方包。
# 可用 sys.path 查看实际搜索路径，但不要在业务代码中随意修改它。
# 标准库随 Python 安装；requests/pandas 等第三方库需用包管理器安装。

def main() -> None:
    """程序入口集中在 main 中，便于测试和复用。"""
    print("只有直接运行本文件时才调用 main()")


# 直接运行时 __name__ == "__main__"；被 import 时 __name__ 是模块名。
# 入口保护防止“导入函数”时意外执行脚本任务，也是多进程程序的重要习惯。
if __name__ == "__main__":
    main()

"""
本节总结：模块负责组织代码，包组织模块；入口保护区分“运行”与“被导入”。
"""
