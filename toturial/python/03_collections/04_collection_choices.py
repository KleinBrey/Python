"""
==================================================
知识点：list、tuple、dict、set 如何选择
==================================================
"""

# list：有序、可修改、允许重复。例：一段时间的收盘价。
closing_prices = [10.2, 10.5, 10.5]

# tuple：有序、不可修改。例：经纬度、RGB、函数的固定多返回值。
price_range = (10.2, 10.8)

# dict：键值映射。例：一只股票的字段，按字段名访问比下标更清楚。
stock = {"symbol": "600519", "price": 1688.0}

# set：唯一元素集合。例：订阅的股票代码，重点是存在性而非顺序。
subscribed_symbols = {"600519", "000001"}

print(closing_prices, price_range, stock, subscribed_symbols)

"""
练习：
1. 五个股票代码按顺序保存，用什么容器？
2. 用户名与年龄的对应关系，用什么容器？
3. 对代码去重，用什么容器？
4. 筛选字典列表中 price > 100 的股票。

# ==========================
# 参考答案
# ==========================
codes = ["600519", "000001", "300750", "002594", "600036"]
user = {"name": "小林", "age": 20}
unique_codes = set(codes + ["600519"])
rows = [{"symbol": "600519", "price": 1688}, {"symbol": "000001", "price": 10.5}]
expensive = [row for row in rows if row["price"] > 100]
print(codes, user, unique_codes, expensive)

本节总结：按“是否有序、是否可改、是否唯一、是否按键查找”选择容器。
"""
