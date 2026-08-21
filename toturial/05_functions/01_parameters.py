"""
==================================================
知识点：位置参数、关键字参数、默认参数、*args 与 **kwargs
==================================================
"""

def create_order(
    symbol: str,
    quantity: int,
    side: str = "buy",
    *,
    remark: str = "",
) -> dict[str, object]:
    """星号后的 remark 只能按关键字传入，调用含义更清楚。"""
    return {"symbol": symbol, "quantity": quantity, "side": side, "remark": remark}


print(create_order("600519", 100))
print(create_order("000001", quantity=200, side="sell", remark="止盈"))


def average(*numbers: float) -> float:
    """*args 把任意数量的位置参数收集为 tuple，类似 JS rest parameters。"""
    print("收到的数字：", numbers)
    if not numbers:
        print("没有提供数字，返回 0.0")
    return sum(numbers) / len(numbers)


print(average(10.2, 10.5, 10.8))


def build_query(**filters: object) -> dict[str, object]:
    """**kwargs 把任意关键字参数收集为 dict，这是 Python 很有特色的写法。"""
    print("收到的过滤条件：", filters)
    return {key: value for key, value in filters.items() if value is not None}


print(build_query(symbol="600519", date=None, limit=20))

# 默认参数只在函数定义时创建一次。可变对象不能直接作为默认值。
def add_symbol(symbol: str, symbols: list[str] | None = None) -> list[str]:
    if symbols is None:
        symbols = []
    symbols.append(symbol)
    return symbols


print(add_symbol("600519"))
print(add_symbol("000001"))  # 不会意外继承上次结果

"""
本节总结：位置参数看顺序，关键字参数看名称；可变默认值用 None 再创建。
"""
