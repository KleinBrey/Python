"""
==================================================
知识点：上下文管理器、__enter__、__exit__ 与 contextmanager
==================================================
"""

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from collections.abc import Iterator

class TracedTask:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self) -> "TracedTask":
        print("开始任务：", self.name)
        return self  # as 后的变量接收这个返回值

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        print("结束任务：", self.name)
        return False  # False 表示不吞掉异常


with TracedTask("读取行情") as task:
    print("执行中：", task.name)


@contextmanager
def temporary_text(content: str) -> Iterator[Path]:
    """yield 前相当于 enter，yield 后 finally 相当于 exit。"""
    with TemporaryDirectory() as directory:
        path = Path(directory) / "demo.txt"
        path.write_text(content, encoding="utf-8")
        yield path


with temporary_text("Python 上下文管理器") as path:
    print(path.read_text(encoding="utf-8"))

# with open(...) 会自动关闭，是因为文件对象实现了上下文管理协议；
# 即使代码块抛异常，__exit__ 仍有机会释放文件句柄。

"""
本节总结：with 保证成对的获取/释放；类协议或 contextmanager 都可创建管理器。
"""
