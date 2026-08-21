"""
==================================================
知识点：可迭代对象、迭代器与生成器
==================================================
"""

prices = [10.2, 10.5, 10.8]  # list 是 iterable，可被 for 遍历
iterator = iter(prices)        # iter() 获取 iterator
print(next(iterator))          # next() 每次取下一个元素
print(next(iterator))

try:
    print(next(iterator))
    print(next(iterator))      # 耗尽后抛 StopIteration，for 会自动处理它
except StopIteration:
    print("迭代器已耗尽")


def price_stream(start: float, count: int):
    """含 yield 的函数调用后返回生成器，不会一次性计算全部结果。"""
    current = start
    for _ in range(count):
        yield round(current, 2)  # 暂停并交出一个值，下次从这里继续
        current += 0.1


for price in price_stream(10.0, 3):
    print("生成：", price)

# return 结束函数并一次性交付结果；yield 可多次交付，适合大文件或数据流。
# 生成器表达式使用圆括号，惰性计算；列表推导式使用方括号，立即创建全部结果。
squares = (number * number for number in range(5))
print(next(squares), list(squares))

"""
本节总结：iter 获取迭代器，next 推进；yield 创建惰性生成器，节省内存。
"""
