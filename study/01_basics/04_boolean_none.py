"""
==================================================
知识点：布尔值、真值判断与 None
==================================================
"""

# 条件语句不要求表达式必须是 bool。0、空字符串、空容器和 None 都是假值；
# 非零数字、非空字符串和非空容器通常是真值。
samples = [0, 1, "", "Python", [], [1], None]
for item in samples:
    print(repr(item), "=>", bool(item))

username = "  "
if username.strip():
    print("用户名有效")
else:
    print("用户名不能为空")

# and/or 会短路：确定结果后就不再计算右侧。
# 这常用于提供默认值，但要留意 0 也会被当成假值。
input_name = ""
display_name = input_name or "匿名用户"
print(display_name)

cached_price = None
if cached_price is None:
    print("缓存未命中，需要重新查询")

# ⚠️ 不要写 if value == True，直接写 if value 更自然。
# ⚠️ 不要用 is 比较普通数字或字符串；is 判断是否为同一个对象。

"""
本节总结：理解真值能写出简洁条件；None 表示缺失值并使用 is None 判断。
"""
