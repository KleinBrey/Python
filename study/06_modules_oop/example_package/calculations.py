"""可复用的行情计算模块；也可以单独运行进行自检。"""

def calculate_change(old_price: float, new_price: float) -> float:
    if old_price <= 0:
        raise ValueError("旧价格必须大于 0")
    return (new_price - old_price) / old_price


if __name__ == "__main__":
    print(f"示例涨跌幅：{calculate_change(100, 105):.2%}")
