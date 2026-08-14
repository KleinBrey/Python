"""
==================================================
知识点：if、elif、else 与嵌套判断
==================================================
"""

change_percent = 3.2

# Python 用缩进界定代码块。if 从上到下判断，只执行第一个满足的分支。
if change_percent >= 5:
    status = "大幅上涨"
elif change_percent > 0:
    status = "上涨"
elif change_percent == 0:
    status = "平盘"
else:
    status = "下跌"
print(status)

is_market_open = True
balance = 10_000
order_amount = 8_000

if is_market_open:
    if balance >= order_amount:
        print("可以买入")
    else:
        print("余额不足")
else:
    print("市场未开盘")

# 简单二选一可用条件表达式，复杂逻辑仍用普通 if 更清楚。
label = "盈利" if change_percent > 0 else "未盈利"
print(label)

# ⚠️ = 是赋值，== 才是相等比较；条件末尾必须有冒号。

"""
本节总结：if/elif/else 只执行一个匹配分支；嵌套不宜过深，可用函数拆分。
"""
