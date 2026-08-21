"""一个最小教学包。

__init__.py 可标记普通包，也可暴露最常用的公共名称。
不要在这里执行耗时任务，否则每次 import 包都会触发。
"""

try:
    # 作为包导入时使用相对导入。
    from .calculations import calculate_change
except ImportError:
    # 直接运行 __init__.py 时没有包上下文，使用同目录绝对导入完成独立演示。
    from calculations import calculate_change

__all__ = ["calculate_change"]

if __name__ == "__main__":
    print(f"包入口自检：{calculate_change(100, 105):.2%}")
