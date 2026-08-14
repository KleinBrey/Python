"""
==================================================
知识点：ABC、abstractmethod 与接口思想
==================================================
"""

from abc import ABC, abstractmethod

class MarketDataProvider(ABC):
    """ABC 表示抽象基类：描述共同契约，不负责提供完整实现。"""

    @abstractmethod
    def fetch_data(self, symbol: str) -> dict[str, object]:
        """abstractmethod 强制可实例化的子类实现此方法。"""
        ...


class MemoryProvider(MarketDataProvider):
    def fetch_data(self, symbol: str) -> dict[str, object]:
        return {"symbol": symbol, "price": 1688.0}


provider = MemoryProvider()
print(provider.fetch_data("600519"))

# 错误示例：MarketDataProvider()  # TypeError：抽象方法尚未实现
# Python 没有 Java/TypeScript 完全相同的 interface 关键字。
# ABC 适合需要运行时约束或共享实现；typing.Protocol 适合结构化“像接口”类型检查。

"""
练习：定义抽象 Storage.save(data)，再写 MemoryStorage 实现它。

# ==========================
# 参考答案
# ==========================
class Storage(ABC):
    @abstractmethod
    def save(self, data: dict[str, object]) -> None:
        ...

class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def save(self, data: dict[str, object]) -> None:
        self.rows.append(data)

storage = MemoryStorage()
storage.save({"symbol": "600519"})
print(storage.rows)

本节总结：抽象类定义必须遵守的契约；未实现抽象方法的子类不能实例化。
"""
