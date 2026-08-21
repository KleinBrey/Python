"""
==================================================
知识点：class、object、属性、方法、self 与 __init__
==================================================
"""

class Stock:
    """类是创建对象的模板；对象是类的具体实例。"""

    market = "A股"  # 类变量由所有实例共享，适合共同且稳定的信息

    def __init__(self, symbol: str, price: float):
        # __init__ 在对象创建后初始化实例状态。
        # self 表示“当前这个对象”，调用时由 Python 自动传入。
        self.symbol = symbol
        self.price = price

    def update_price(self, new_price: float) -> None:
        """实例方法能通过 self 读取和修改当前实例。"""
        if new_price <= 0:
            raise ValueError("价格必须大于 0")
        self.price = new_price

    def market_value(self, quantity: int) -> float:
        return self.price * quantity

    @staticmethod
    def change_value(data:int) -> float:
        return data * 2


maotai = Stock("600519", 1688.0)
pingan = Stock("000001", 10.5)
maotai.update_price(1690.0)
print(maotai.change_value(108))
print(maotai.symbol, maotai.market_value(100), maotai.market)
print(pingan.symbol, pingan.price, pingan.market)

# JS 的 this 与 Python self 用途相近；区别是 self 必须显式写在方法参数中。

"""
本节总结：类定义行为和数据结构；self 指向当前实例；实例变量彼此独立。
"""
