"""
==================================================
知识点：元组 Tuple 与解包
==================================================

tuple 与 list 都有顺序；tuple 创建后不能增删改，适合表达结构固定的数据。
"""

quote = ("600519", 1688.0, 1000)
print(quote[0], len(quote))

# 单元素元组必须有逗号，否则括号只是普通分组。
one_item = ("600519",)
print(type(one_item))

symbol, price, volume = quote  # 解包要求变量数与元素数相同
print(symbol, price, volume)

first, *middle, last = [1, 2, 3, 4]
print(first, middle, last)  # *middle 接收剩余元素，结果是 list

def get_price_range() -> tuple[float, float]:
    # “多返回值”本质是返回一个元组。
    return 10.2, 10.8

low, high = get_price_range()
print(low, high)

# 交换变量无需临时变量，右侧先组成元组再解包。
low, high = high, low
print(low, high)

"""
本节总结：tuple 不可修改；逗号比括号更关键；解包让结构化赋值更清晰。
"""
