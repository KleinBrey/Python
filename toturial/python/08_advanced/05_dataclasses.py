"""
==================================================
知识点：dataclass
==================================================
"""

from dataclasses import asdict, dataclass, field

@dataclass(slots=True)
class Stock:
    """装饰器自动生成 __init__、__repr__、__eq__ 等样板代码。"""
    symbol: str
    price: float
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # 自动 __init__ 完成后执行，适合运行时校验或标准化。
        self.symbol = self.symbol.upper()
        if self.price <= 0:
            raise ValueError("价格必须大于 0")


stock = Stock("600519.sh", 1688.0)
stock.tags.append("白酒")
same = Stock("600519.SH", 1688.0, ["白酒"])
print(stock)
print(stock == same)
print(asdict(stock))

# default_factory 每个实例创建独立 list，避免共享可变默认值。
# 普通 class 适合复杂生命周期/高度自定义行为；dataclass 适合以数据为中心的对象。
# frozen=True 可创建不可变风格的数据对象；slots=True 可减少属性拼写错误和内存。

"""
本节总结：dataclass 减少数据类样板代码；可变默认字段必须用 default_factory。
"""
