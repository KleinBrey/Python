"""
==================================================
知识点：运算符
==================================================
"""

price = 105
price += 5  # 等价于 price = price + 5
print(price)

# 比较运算可以链式书写，这一点比 JS 更接近数学表达式。
print(0 < price < 200)
print(price == 110, price != 100, price >= 100)

has_account = True
has_permission = False
print(has_account and has_permission)
print(has_account or has_permission)
print(not has_permission)

symbols = ["600000", "000001"]
print("600000" in symbols)       # in 判断成员是否存在
print("300750" not in symbols)

first = [1, 2]
second = first
third = [1, 2]
print(first == third)  # True：内容相同
print(first is third)  # False：不是同一个对象
print(first is second) # True：指向同一个对象

# 优先级不确定时加括号，可读性比炫技更重要。
is_tradeable = (price > 0) and ("600000" in symbols)
print(is_tradeable)

"""
本节总结：== 比内容，is 比身份；in 查成员；逻辑运算符会短路。
"""
