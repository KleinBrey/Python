"""
==================================================
知识点：定义、调用、参数、返回值与类型注解
==================================================
"""

def get_user(name: str, age: int) -> dict[str, object]:
    """创建用户字典。

    name: str 表示希望 name 是字符串；age: int 表示希望 age 是整数；
    -> dict[str, object] 表示返回“字符串键、任意对象值”的字典。
    注解主要服务阅读器、IDE 和类型检查器，Python 默认不会在运行时强制检查。
    """
    return {"name": name, "age": age}


user = get_user("小林", 20)
print(user)


def calculate_return(buy_price: float, sell_price: float) -> float:
    """计算收益率；return 会立刻结束函数并把结果交给调用者。"""
    if buy_price <= 0:
        raise ValueError("买入价必须大于 0")
    return (sell_price - buy_price) / buy_price


rate = calculate_return(100, 110)
print(f"收益率：{rate:.2%}")


def print_notice(message: str) -> None:
    """-> None 表示函数只做动作，不打算返回有意义的结果。"""
    print("通知：", message)


result = print_notice("学习函数")
print("无显式 return 时返回：", result)

"""
本节总结：函数封装可复用逻辑；参数接收输入，return 交付输出；注解不强制类型。
"""
