"""
==================================================
知识点：match / case（Python 3.10+）
==================================================

match 不只是其他语言的 switch，它支持结构模式匹配；简单状态分支最易理解。
"""

order_status = "filled"
match order_status:
    case "pending":
        message = "订单等待处理"
    case "filled":
        message = "订单已成交"
    case "cancelled" | "rejected":
        message = "订单未成交"
    case _:  # _ 是兜底模式，类似 else/default
        message = "未知状态"
print(message)

# 结构匹配可以同时检查字典形状并提取值。
event = {"type": "price", "symbol": "600519", "value": 1688.0}
match event:
    case {"type": "price", "symbol": symbol, "value": value}:
        print(f"{symbol} 最新价 {value}")
    case {"type": event_type}:
        print(f"暂不处理事件：{event_type}")
    case _:
        print("事件格式错误")

"""
本节总结：少量范围判断用 if；针对明确形状或枚举值分支可考虑 match。
"""
