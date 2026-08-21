"""
==================================================
知识点：集合 Set
==================================================

set 无重复元素，不支持下标，适合去重和集合关系运算。
"""

symbols = {"600519", "000001", "600519"}
print(symbols)  # 重复值只保留一个；显示顺序不应依赖

symbols.add("300750")
symbols.remove("000001")   # 不存在会 KeyError
symbols.discard("999999")  # 不存在也不会报错，更适合不确定场景
print(symbols)

watchlist_a = {"600519", "300750", "000001"}
watchlist_b = {"600519", "002594"}
print("并集：", watchlist_a | watchlist_b)
print("交集：", watchlist_a & watchlist_b)
print("差集：", watchlist_a - watchlist_b)
print(watchlist_a.union(watchlist_b))
print(watchlist_a.intersection(watchlist_b))
print(watchlist_a.difference(watchlist_b))

unique_symbols = set(["600519", "600519", "000001"])
print(unique_symbols)

# 空集合必须写 set()；{} 创建的是空字典。
empty_set = set()
print(type(empty_set))

"""
本节总结：set 用于去重、成员判断、并交差运算；无序且不能按下标访问。
"""
