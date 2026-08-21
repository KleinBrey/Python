"""
==================================================
知识点：for、range、enumerate 与 zip
==================================================
"""

symbols = ["600519", "000001", "300750"]

# Python for 直接遍历元素，不需要手工维护下标。
for symbol in symbols:
    print("查询：", symbol)

# enumerate(iterable, start=1) 同时给出序号和值。
# 它比 range(len(symbols)) 更清楚，也不易出现下标错误。
for index, value in enumerate(symbols, start=1):
    print(f"第 {index} 只股票是 {value}")

# range 的结束值不包含在内，与切片规则一致。
print(list(range(0, 10, 2)))

prices = [1688.0, 10.5, 220.0]
# zip 将多个可迭代对象按位置配对；默认在最短输入耗尽时停止。
print(list(zip(symbols, prices)))
for symbol, price in zip(symbols, prices):
    print(f"{symbol}: {price:.2f}")

stock = {"symbol": "600519", "price": 1688.0}
for key, value in stock.items():
    # items() 产生二元组，for 在每轮把二元组解包给 key 和 value。
    print(key, value)

# for...else 的 else 在循环没有被 break 时执行，实际项目中可用于查找。
target = "000001"
for symbol in symbols:
    if symbol == target:
        print("找到了", target)
        break
else:
    print("没有找到")

"""
本节总结：直接遍历值；需要序号用 enumerate；并行遍历用 zip。
"""
