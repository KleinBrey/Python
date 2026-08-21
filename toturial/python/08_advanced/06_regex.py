"""
==================================================
知识点：正则表达式 re
==================================================

正则适合按模式查找/替换文本；简单的固定判断优先 startswith、split 等字符串方法。
"""

import re

text = "股票 600519 和 000001 今日更新"
print(re.search(r"\d{6}", text).group())  # search 在任意位置找第一个匹配
print(re.findall(r"\d{6}", text))        # findall 返回所有匹配文本

print(re.match(r"股票", text).group())    # match 只从字符串开头尝试
cleaned = re.sub(r"\s+", " ", "价格   1688.0\n成交量  100")
print(cleaned)
print(re.split(r"[,;，；]", "600519,000001；300750"))

email_pattern = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
for email in ["user@example.com", "not-an-email"]:
    print(email, bool(email_pattern.fullmatch(email)))

phone = "13812345678"
masked = re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", phone)
print(masked)

# raw string r"..." 避免 Python 和正则都处理反斜杠，更容易阅读。
# 正则邮箱示例仅用于基础演示，生产环境的完整邮箱规则远比这里复杂。

"""
练习：从“SH600519 SZ000001”中找出两个 6 位数字代码（模式写作反斜杠+d{6}）。

# ==========================
# 参考答案
# ==========================
print(re.findall(r"\\d{6}", "SH600519 SZ000001"))

本节总结：search 找一个、findall 找全部、sub 替换、split 按模式拆分。
"""
