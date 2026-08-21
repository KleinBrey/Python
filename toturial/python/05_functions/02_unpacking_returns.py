"""
==================================================
知识点：参数解包与多返回值
==================================================
"""

def quote(symbol: str, price: float, volume: int = 0) -> str:
    return f"{symbol}: price={price:.2f}, volume={volume}"


# * 对序列做位置参数解包；元素个数和顺序必须与参数兼容。
positional_data = ["600519", 1688.0, 1000]
print(quote(*positional_data))

# ** 对字典做关键字参数解包；键名必须匹配参数名。
keyword_data = {"symbol": "000001", "price": 10.5, "volume": 5000}
print(quote(**keyword_data))


def summarize(values: list[float]) -> tuple[float, float, float]:
    """Python 的多返回值实际上是一个 tuple。"""
    return min(values), max(values), sum(values) / len(values)


low, high, mean = summarize([10.2, 10.8, 10.5])
print(f"最低={low}，最高={high}，平均={mean:.2f}")

# 合并字典：右侧相同键覆盖左侧。Python 3.9+ 也可使用 | 运算符。
defaults = {"timeout": 10, "retries": 3}
custom = {"timeout": 5}
config = {**defaults, **custom}
print(config, defaults | custom)

"""
本节总结：* 展开位置参数，** 展开关键字参数；多返回值通过 tuple 解包接收。
"""


