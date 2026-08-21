"""学习上下文管理器：让资源在使用后自动清理。"""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


# 写法一：在类中实现 __enter__ 和 __exit__。
class TracedTask:
    """记录一个任务何时开始、何时结束。"""

    def __init__(self, name: str):
        self.name = name

    def __enter__(self) -> "TracedTask":
        """进入 with 代码块时自动调用。"""

        print("开始任务：", self.name)

        # 返回值会交给 with 后面的 as 变量。
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """离开 with 代码块时自动调用，即使代码报错也会调用。"""

        print("结束任务：", self.name)

        # 返回 False：如果 with 中出现异常，继续把异常抛给外层。
        return False


# 执行顺序：__enter__ -> with 内的代码 -> __exit__。
with TracedTask("读取行情") as task:
    print("执行中：", task.name)


# 写法二：用 @contextmanager 把生成器变成上下文管理器。
@contextmanager
def temporary_text(content: str) -> Generator[Path, None, None]:
    """创建临时文本文件，使用结束后自动删除。"""

    # TemporaryDirectory 离开 with 后会自动删除临时文件夹。
    with TemporaryDirectory() as directory:
        file_path = Path(directory) / "demo.txt"
        file_path.write_text(content, encoding="utf-8")

        # yield 前面的代码相当于 __enter__。
        # file_path 会交给 with 后面的 as 变量。
        yield file_path

        # yield 后面的代码相当于 __exit__。
        # 本例不需要手动删除，TemporaryDirectory 会负责清理。


with temporary_text("Python 上下文管理器") as path:
    text = path.read_text(encoding="utf-8")
    print(text)


# 常见例子：
# with open("demo.txt") as file:
#     content = file.read()
#
# 离开 with 后，文件会自动关闭。
#
# 总结：with 可以保证“开始时获取资源，结束时释放资源”成对执行。
