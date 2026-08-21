"""
==================================================
知识点：基本数据类型、type() 与 isinstance()
==================================================
"""

age = 20                  # int：整数，大小通常只受内存限制
price = 12.75             # float：浮点数，适合一般科学计算，但有二进制精度限制
name = "小林"             # str：Unicode 字符串
is_active = True          # bool：只有 True 和 False，首字母必须大写
missing_value = None      # None：表示“没有值”，类似 JS 的 null

for value in [age, price, name, is_active, missing_value]:
    print(repr(value), "的类型是", type(value))

# type(x) == int 只匹配精确类型；isinstance 会考虑继承，日常判断更推荐后者。
print(isinstance(age, int))
print(isinstance(price, (int, float)))  # 可同时判断多个候选类型

# bool 是 int 的子类，这是 Python 的历史设计，因此下面结果是 True。
print(isinstance(True, int))

# None 要用 is 判断身份，不要写 == None。
if missing_value is None:
    print("数据暂时不存在")

"""
本节总结：常见标量类型有 int、float、str、bool 和 None；
type() 查看精确类型，isinstance() 更适合做类型判断。
"""
