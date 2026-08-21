"""
==================================================
知识点：现代 Python 类型注解
==================================================
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, TypeAlias

name: str = "小林"
age: int = 20
prices: list[float] = [10.2, 10.5]
user: dict[str, str] = {"name": "小林"}
nickname: str | None = None  # Python 3.10+，表示 str 或 None

StockRow: TypeAlias = dict[str, str | float]

def get_data(limit: int = 10) -> list[StockRow]:
    return [{"symbol": "600519", "price": 1688.0}][:limit]

def apply(value: float, operation: Callable[[float], float]) -> float:
    return operation(value)

mode: Literal["daily", "weekly"] = "daily"  # 仅允许两个字面值，适合有限选项
untyped_payload: Any = {"unknown": [1, "two"]}  # Any 关闭该处检查，应谨慎使用

print(name, age, prices, user, nickname, get_data())
print(apply(10, lambda value: value * 1.1), mode, untyped_payload)

# Optional[str] 等价于 str | None；Union[int, str] 等价于 int | str。
# from __future__ import annotations 会延迟注解求值：
# 能更自然地引用尚未定义的类，并减少部分运行时导入问题；3.11 项目中仍常见。

"""
本节总结：注解记录数据形状并帮助工具发现错误，但默认不做运行时校验。
"""
