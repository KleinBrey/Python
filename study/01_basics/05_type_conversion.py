"""
==================================================
知识点：类型转换
==================================================
"""

text_price = "12.50"
price = float(text_price)
quantity = int("100")
print(price * quantity)

print(str(2026))       # 变成文本，常用于拼接或存储
print(int(3.9))        # 截掉小数部分，不是四舍五入
print(float(10))
print(list("ABC"))    # ['A', 'B', 'C']
print(tuple([1, 2]))
print(set([1, 1, 2]))  # 集合会去重

# 用户输入、CSV 和环境变量通常都是字符串，转换前应考虑非法内容。
raw_age = "二十"
try:
    age = int(raw_age)
except ValueError:
    print(f"{raw_age!r} 不是有效整数")

# bool("False") 是 True，因为它是非空字符串；不能用它解析文本真假。
raw_enabled = "false"
enabled = raw_enabled.strip().lower() in {"true", "1", "yes"}
print("是否启用：", enabled)

"""
本节总结：int/float/str/bool 负责转换；外部输入转换可能抛出 ValueError。
"""
