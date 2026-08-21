"""
==================================================
知识点：Python 列表 List
==================================================

list ≈ JavaScript Array：有顺序、可重复、可修改，可存放不同类型。
实际项目更建议同一列表保存同类数据。
"""

prices = [10.2, 10.5, 10.3]
print(prices[0], prices[-1], prices[1:])

prices[1] = 10.6          # 修改指定位置
prices.append(10.8)       # 末尾添加一个对象
prices.extend([11.0, 11.2])  # 添加多个元素；与 append([..]) 不同
prices.insert(1, 10.4)    # 在指定下标插入
print(prices)

prices.remove(10.3)       # 按值删除第一个匹配项；不存在会 ValueError
last = prices.pop()       # 默认删除并返回末尾元素
print("弹出：", last)
print("10.2 出现次数：", prices.count(10.2))
print("10.8 所在下标：", prices.index(10.8))

ascending = sorted(prices)  # 返回新列表，不改原数据
prices.sort(reverse=True)   # 原地排序，返回 None
prices.reverse()            # 原地反转
copied = prices.copy()      # 浅拷贝；新列表与原列表不是同一个对象
print(ascending, prices, copied)

for index, value in enumerate(prices, start=1):
    print(f"第 {index} 个价格：{value}")

matrix = [["600519", 1688.0], ["000001", 10.5]]
print(matrix[0][1])

# 推导式适合“从一个可迭代对象生成新列表”的简单映射/筛选。
high_prices = [value for value in prices if value >= 10.5]
print(high_prices)

temporary = [1, 2]
temporary.clear()
print(temporary)

# ⚠️ prices[100] 会 IndexError；删除前可先用 in 检查。
# ⚠️ copied = prices 不是复制，两变量会指向同一列表。

"""
本节总结：append 加一个，extend 加多个；sort 原地改，sorted 返回新列表。
"""
