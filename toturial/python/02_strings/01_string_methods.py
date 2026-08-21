"""
==================================================
知识点：常用字符串方法
==================================================
"""

raw_line = " 600519,贵州茅台,1688.50 \n"
clean_line = raw_line.strip()  # 删除两端空白，不会删除中间空格
parts = clean_line.split(",")
print(parts)

symbol, name, price = parts
print(symbol, name, price)
print(" | ".join(parts))  # join 由“分隔符”调用，连接一组字符串

message = "Python is friendly"
print(message.find("is"))      # 找不到返回 -1，适合“可能不存在”
print(message.index("is"))     # 找不到抛 ValueError，适合“必须存在”
print(message.replace("friendly", "powerful"))
print(message.startswith("Python"), message.endswith("ly"))
print(message.upper(), message.lower())

# 常见清洗案例：将用户输入的股票代码标准化。
raw_symbols = " 600519.sh, 000001.sz,600519.SH "
symbols = []
for item in raw_symbols.split(","):
    normalized = item.strip().upper()
    if normalized and normalized not in symbols:
        symbols.append(normalized)
print("标准化结果：", symbols)

# ⚠️ split() 返回 list；join() 的成员必须都是 str。
# 错误示例：",".join([1, 2])  # TypeError

"""
本节总结：strip 清边缘、split 拆分、join 连接；find 和 index 的失败行为不同。
"""
