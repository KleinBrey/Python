"""
==================================================
知识点：继承、super、重写与多态
==================================================
"""

class DataProvider:
    def __init__(self, name: str):
        self.name = name

    def fetch_price(self, symbol: str) -> float:
        raise NotImplementedError("子类需要实现 fetch_price")


class ApiProvider(DataProvider):
    def __init__(self, endpoint: str):
        super().__init__("API 数据源")  # 调用父类初始化，避免复制公共逻辑
        self.endpoint = endpoint

    def fetch_price(self, symbol: str) -> float:
        # 重写父类方法；教学示例返回固定数据，不依赖网络。
        return {"600519": 1688.0}.get(symbol, 0.0)


class CacheProvider(DataProvider):
    def __init__(self, cache: dict[str, float]):
        super().__init__("缓存数据源")
        self.cache = cache

    def fetch_price(self, symbol: str) -> float:
        return self.cache.get(symbol, 0.0)


def show_price(provider: DataProvider, symbol: str) -> None:
    # 多态：调用者只依赖共同方法，不关心具体是哪一种 provider。
    print(provider.name, symbol, provider.fetch_price(symbol))


show_price(ApiProvider("https://example.invalid"), "600519")
show_price(CacheProvider({"600519": 1690.0}), "600519")

# 继承表达“是一个”；仅为复用代码时，组合对象常比深层继承更清晰。

"""
本节总结：子类继承并可重写父类行为；super 复用初始化；多态降低调用者耦合。
"""
