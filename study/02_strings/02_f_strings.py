"""
==================================================
知识点：f-string、format 与字符串拼接
==================================================
"""

name = "贵州茅台"
age = 25
price = 1688.5
change = 0.02345

# f 前缀允许在 {} 中写表达式。它类似 JS 模板字符串，但使用花括号插值。
print(f"{name} 上市约 {age} 年，当前价格 {price} 元")
print(f"价格：{price:.2f}")          # .2f：固定两位小数
print(f"涨跌幅：{change:.2%}")       # .2%：乘 100 并显示百分号
print(f"成交额：{12345678.9:,.2f}")  # ,：千位分隔符
print(f"代码调试：{price=}")          # Python 3.8+，同时输出变量名和值

# format() 在动态模板或维护旧代码时仍会见到。
template = "股票：{name}，价格：{price:.2f}"
print(template.format(name=name, price=price))

# 少量固定字符串可用 +，许多片段优先 join，避免重复创建中间字符串。
full_name = "A股-" + name
columns = ["symbol", "date", "close"]
print(full_name, ",".join(columns))

"""
练习：用 f-string 输出“600519 的价格是 1688.50，涨跌幅是 2.35%”。

# ==========================
# 参考答案
# ==========================
symbol = "600519"
print(f"{symbol} 的价格是 {price:.2f}，涨跌幅是 {change:.2%}")

本节总结：f-string 是现代 Python 首选格式化方式，冒号后可写格式规则。
"""
