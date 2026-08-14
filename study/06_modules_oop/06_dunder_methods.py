"""
==================================================
知识点：__str__ 与 __repr__
==================================================
"""

class Stock:
    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price

    def __str__(self) -> str:
        """面向最终用户的友好文本，print(obj) 优先使用。"""
        return f"股票 {self.symbol}，价格 {self.price:.2f} 元"

    def __repr__(self) -> str:
        """面向开发者的明确文本，理想情况下能帮助重建或诊断对象。"""
        return f"Stock(symbol={self.symbol!r}, price={self.price!r})"


stock = Stock("600519", 1688.0)
print(str(stock))
print(repr(stock))
print([stock])  # 容器展示成员时通常使用 repr

"""
本节总结：str 重可读，repr 重明确；双下划线方法让自定义类融入 Python 语法。
"""
