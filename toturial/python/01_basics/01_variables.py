"""
==================================================
知识点：变量与命名
==================================================

变量可以理解为“指向某个对象的名字”。Python 无须用 let/const 声明类型，
解释器会在赋值时让名字引用对应对象。
"""

stock_name = "贵州茅台"
stock_price = 1688.50
holding_quantity = 10
is_profitable = True

print(stock_name, stock_price, holding_quantity, is_profitable)

# 同一个变量名可以重新绑定到另一个对象，但实际项目中不要随意改变其含义，
# 否则阅读代码和类型检查都会变困难。
stock_price = 1692.00
print(f"更新后的价格：{stock_price}")

# 多重赋值适合含义紧密的少量数据；左右数量必须一致。
open_price, close_price = 1680.0, 1692.0
print(open_price, close_price)

# 常量在 Python 中没有语法强制，社区约定使用全大写提示“不要修改”。
TRADING_DAYS_PER_YEAR = 250

# 推荐 snake_case（小写加下划线）；名称不能数字开头，也不能使用 if、class 等关键字。
# 错误示例：2price = 10       # SyntaxError
# 不推荐：p = 10              # 含义不清

"""
练习：创建 symbol、price、volume 三个变量并打印成交额。

# ==========================
# 参考答案
# ==========================
symbol = "600000"
price = 10.5
volume = 1000
print(symbol, price * volume)

本节总结：变量是对象的名字；使用 snake_case；常量名用全大写。
"""
