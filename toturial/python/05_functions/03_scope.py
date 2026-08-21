"""
==================================================
知识点：作用域、global 与 nonlocal
==================================================

Python 查找名字遵循 LEGB：Local、Enclosing、Global、Built-in。
"""

tax_rate = 0.001  # 全局变量，函数可以读取

def calculate_fee(amount: float) -> float:
    fee = amount * tax_rate  # fee 是局部变量，函数外不可见
    return fee


print(calculate_fee(10_000))

request_count = 0

def record_request() -> None:
    global request_count  # 声明要重新绑定模块级变量
    request_count += 1


record_request()
print(request_count)


def make_counter():
    count = 0

    def increment() -> int:
        nonlocal count  # 重新绑定外层函数的局部变量，不是全局变量
        count += 1
        return count

    return increment


counter = make_counter()
print(counter(), counter())

# 实际项目尽量用参数和返回值传递数据；大量 global 会让状态难追踪、难测试。

"""
本节总结：变量默认局部；global 修改模块变量，nonlocal 修改闭包外层变量，均应慎用。
"""
