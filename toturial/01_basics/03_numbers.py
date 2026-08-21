"""
==================================================
知识点：数字与数值计算
==================================================
"""

from decimal import Decimal

price = 10.5
quantity = 200
amount = price * quantity
print(f"成交额：{amount:,.3f} 元")

print(7 / 2)   # / 总是得到浮点结果 3.5
print(7 // 2)  # // 向下取整得到 3
print(7 % 2)   # % 取余数，常用来判断奇偶
print(2 ** 10) # ** 幂运算

# round() 用于显示层面的四舍五入，但浮点数不能精确表示所有十进制小数。
print(0.1 + 0.2)  # 可能显示 0.30000000000000004，并非 Python 算错
print(round(0.1 + 0.2, 2))

# 金额计算对精度严格时，用字符串创建 Decimal，避免先产生 float 误差。
exact_amount = Decimal("10.10") * Decimal("3")
print("精确金额：", exact_amount)

# 常用内置函数。
prices = [10.2, 10.8, 10.5]
print(min(prices), max(prices), sum(prices), abs(-3.5))

"""
本节总结：/、//、%、** 含义不同；float 有精度边界，严格金额用 Decimal。
"""
