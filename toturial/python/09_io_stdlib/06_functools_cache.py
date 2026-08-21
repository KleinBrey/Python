"""
==================================================
知识点：functools、lru_cache、partial 与 reduce
==================================================
"""

from functools import lru_cache, partial, reduce
from operator import mul

@lru_cache(maxsize=128)
def fibonacci(number: int) -> int:
    """缓存相同参数的结果，避免重复计算。参数必须可哈希。"""
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


print(fibonacci(20))
print(fibonacci.cache_info())

def calculate_fee(amount: float, rate: float) -> float:
    return amount * rate


# partial 固定部分参数，创建更具体的新函数。
stock_fee = partial(calculate_fee, rate=0.001)
print(stock_fee(10_000))

# reduce 累积合并序列；简单求和/乘积优先 sum/math.prod，意图更直接。
print(reduce(mul, [2, 3, 4], 1))

# ⚠️ lru_cache 不适合结果频繁变化、参数不可哈希或缓存对象很大的函数。

"""
本节总结：lru_cache 是记忆结果的装饰器；partial 预填参数；缓存需考虑失效策略。
"""
