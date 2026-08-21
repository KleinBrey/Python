"""
==================================================
知识点：实例方法、类方法与静态方法
==================================================
"""

class Stock:
    exchange_suffix = ".SH"

    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price

    def display(self) -> str:
        """实例方法接收 self，处理某个对象的状态。"""
        return f"{self.symbol}: {self.price:.2f}"

    @classmethod
    def from_text(cls, text: str) -> "Stock":
        """类方法接收 cls，常用作替代构造器；子类调用时也能创建子类。"""
        symbol, raw_price = text.split(",")
        return cls(symbol.strip(), float(raw_price))

    @staticmethod
    def is_valid_symbol(symbol: str) -> bool:
        """静态方法不接收 self/cls，只是逻辑上属于该类的工具函数。"""
        return symbol.isdigit() and len(symbol) == 6


stock = Stock.from_text("600519, 1688.50")
print(stock.display())
print(Stock.is_valid_symbol(stock.symbol))

# 不要为了“面向对象”把所有工具都塞进 staticmethod；独立模块函数通常更简单。

"""
本节总结：需要对象状态用实例方法；替代构造器用 classmethod；纯工具可用 staticmethod。
"""
