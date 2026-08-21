"""
==================================================
知识点：函数对象、闭包、装饰器与 wraps
==================================================
"""

from functools import wraps
from time import perf_counter
from typing import Callable, TypeVar

R = TypeVar("R")

def timer(func: Callable[..., R]) -> Callable[..., R]:
    """装饰器接收函数，并返回一个增加了计时行为的新函数。"""
    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> R:
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = perf_counter() - start
            print(f"{func.__name__} 用时 {elapsed:.6f} 秒")
    return wrapper


@timer
def calculate_total(prices: list[float]) -> float:
    return sum(prices)


print(calculate_total([10.2, 10.5, 10.8]))
print("函数名仍是：", calculate_total.__name__)  # wraps 保留原函数元数据


def repeat(times: int):
    """带参数装饰器需要多一层函数，用闭包记住 times。"""
    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        @wraps(func)
        def wrapper() -> None:
            for _ in range(times):
                func()
        return wrapper
    return decorator


@repeat(2)
def say_hello() -> None:
    print("你好")


say_hello()

# @timer 等价于 calculate_total = timer(calculate_total)。
# @lru_cache 也是装饰器：它返回一个会记住调用结果的包装函数。

"""
本节总结：装饰器在不修改原函数主体的前提下添加通用行为；务必使用 wraps。
"""
