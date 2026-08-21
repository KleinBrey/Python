"""
==================================================
知识点：math、random 与 statistics
==================================================
"""

import math
import random
import statistics

print(math.sqrt(16), math.ceil(3.2), math.floor(3.8), math.isclose(0.1 + 0.2, 0.3))

prices = [10.2, 10.5, 10.8, 10.5]
print("均值：", statistics.mean(prices))
print("中位数：", statistics.median(prices))
print("总体标准差：", statistics.pstdev(prices))

# 固定 seed 让教学/测试结果可复现。安全令牌和密码不能用 random，应使用 secrets。
rng = random.Random(42)
print("模拟价格：", round(rng.uniform(10, 11), 2))
print("随机抽样：", rng.sample(["A", "B", "C", "D"], k=2))

"""
本节总结：math 做数学计算，statistics 做基础统计，random 适合模拟而非安全用途。
"""
