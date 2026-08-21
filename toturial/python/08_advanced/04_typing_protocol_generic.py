"""
==================================================
知识点：Protocol、Generic 与 TypeVar
==================================================
"""

from typing import Generic, Protocol, TypeVar

class PriceProvider(Protocol):
    """结构化接口：对象只要“长得像”这个协议即可，无须显式继承。"""
    def get_price(self, symbol: str) -> float:
        ...


class MemoryPrices:
    def get_price(self, symbol: str) -> float:
        return {"600519": 1688.0}.get(symbol, 0.0)


def print_price(provider: PriceProvider, symbol: str) -> None:
    print(symbol, provider.get_price(symbol))


print_price(MemoryPrices(), "600519")

T = TypeVar("T")

class Repository(Generic[T]):
    """T 是占位类型，让一个仓库保持“存入什么类型，就取出什么类型”。"""
    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def all(self) -> list[T]:
        return self._items.copy()


stock_repository: Repository[dict[str, object]] = Repository()
stock_repository.add({"symbol": "600519", "price": 1688.0})
print(stock_repository.all())

"""
本节总结：Protocol 描述所需能力；Generic/TypeVar 在复用代码时保留具体类型信息。
"""
