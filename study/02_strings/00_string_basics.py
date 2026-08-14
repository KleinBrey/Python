"""
==================================================
知识点：字符串创建、索引、切片与不可变性
==================================================
"""

single = '单引号字符串'
double = "双引号字符串"
multi = """这是多行字符串，
换行会保留。"""
print(single, double, multi, sep="\n")

symbol = "600519.SH"
# 下标从 0 开始；负下标从末尾倒数。切片 [start:stop:step] 不包含 stop。
print(symbol[0])      # 第一个字符
print(symbol[-1])     # 最后一个字符
print(symbol[:6])     # 从开头取到下标 6 之前
print(symbol[7:])     # 从下标 7 取到结尾
print(symbol[::-1])   # 步长 -1，反转字符串
print(len(symbol))

# str 不可变：方法返回新字符串，原字符串没有被修改。
name = "python"
upper_name = name.upper()
print(name, upper_name)
# 错误示例：name[0] = "P"  # TypeError

# 转义字符让引号、换行、制表符具有特殊含义。
print("第一行\n第二行\t缩进")
# raw string 通常用于 Windows 路径或正则；反斜杠大多按普通字符处理。
pattern = r"\d{6}"
print(pattern)

"""
本节总结：字符串有序但不可修改；切片不包含结束位置；raw string 常用于正则。
"""
