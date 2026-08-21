"""
==================================================
知识点：常用设计模式（股票行情场景）
==================================================

模式是反复出现问题的命名解法，不是必须套用的模板。
"""

from typing import Protocol

class PriceProvider(Protocol):
    """Provider Pattern：隔离外部行情来源。"""
    def fetch(self, symbol: str) -> float: ...


class MemoryProvider:
    def fetch(self, symbol: str) -> float:
        return {"600519": 1688.0}.get(symbol, 0.0)


class PriceRepository(Protocol):
    """Repository Pattern：隔离数据保存与查询细节。"""
    def save(self, symbol: str, price: float) -> None: ...
    def get(self, symbol: str) -> float | None: ...


class MemoryRepository:
    def __init__(self) -> None:
        self.data: dict[str, float] = {}

    def save(self, symbol: str, price: float) -> None:
        self.data[symbol] = price

    def get(self, symbol: str) -> float | None:
        return self.data.get(symbol)


class StockService:
    """Service Layer：编排业务流程，不关心网络/数据库细节。

    构造器接收依赖就是 Dependency Injection（依赖注入）的基础形式。
    """
    def __init__(self, provider: PriceProvider, repository: PriceRepository):
        self.provider = provider
        self.repository = repository

    def refresh(self, symbol: str) -> float:
        price = self.provider.fetch(symbol)
        if price <= 0:
            raise ValueError("无有效行情")
        self.repository.save(symbol, price)
        return price


def create_provider(mode: str) -> PriceProvider:
    """Factory Pattern：把“创建哪个实现”的判断集中起来。"""
    if mode == "memory":
        return MemoryProvider()
    raise ValueError(f"未知数据源：{mode}")


repository = MemoryRepository()
service = StockService(create_provider("memory"), repository)
print(service.refresh("600519"), repository.get("600519"))

# Singleton 思想：全局只有一个共享实例。它可能隐藏依赖并让测试互相影响，
# 配置/连接池通常由应用入口创建一次再注入，比手写 Singleton 类更容易维护。

"""
本节总结：Provider 隔离外部源，Repository 隔离存储，Service 编排，Factory 负责创建。
"""
