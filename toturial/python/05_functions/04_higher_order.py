"""
==================================================
知识点：lambda、map、filter、sorted、高阶函数与回调
==================================================
"""

stocks = [
    {"symbol": "600519", "price": 1688.0},
    {"symbol": "000001", "price": 10.5},
    {"symbol": "300750", "price": 220.0},
]

# 函数也是对象，可以赋值、放入容器、作为参数或返回值。
def get_price(stock: dict[str, object]) -> float:
    return float(stock["price"])


print(sorted(stocks, key=get_price))
print(sorted(stocks, key=lambda item: float(item["price"]), reverse=True))

# lambda 只能写一个表达式，适合短小的一次性函数；复杂逻辑请使用 def。
prices = list(map(lambda item: item["price"], stocks))
expensive = list(filter(lambda item: item["price"] > 100, stocks))
print(prices, expensive)

# Python 中推导式往往比 map/filter 更直观。
price_list = [stock["price"] for stock in stocks]
expensive_list = [stock for stock in stocks if stock["price"] > 100]
print(price_list, expensive_list)

def process_stock(stock: dict[str, object], callback) -> None:
    """callback 是处理完成后要调用的函数。"""
    print("正在处理", stock["symbol"])
    callback(stock)


def on_complete(stock: dict[str, object]) -> None:
    print("处理完成", stock["symbol"])


process_stock(stocks[0], on_complete)

"""
练习：按 symbol 排序；筛出 price < 100；用推导式取出所有 symbol。

# ==========================
# 参考答案
# ==========================
print(sorted(stocks, key=lambda item: item["symbol"]))
print([item for item in stocks if item["price"] < 100])
print([item["symbol"] for item in stocks])

本节总结：接收或返回函数的是高阶函数；lambda 只用于简单表达式；排序 key 很常用。
"""
