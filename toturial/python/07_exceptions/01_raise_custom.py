"""
==================================================
知识点：raise 与自定义异常
==================================================
"""

class ApiError(RuntimeError):
    """API 调用在运行过程中失败。

    继承 RuntimeError 是因为它描述“程序可运行，但运行时外部操作失败”。
    也可直接继承 Exception；选择父类主要为了让调用者按类别捕获。
    """


class InvalidSymbolError(ValueError):
    """股票代码格式不合法，本质属于值错误。"""


def fetch_price(symbol: str) -> float:
    if not (symbol.isdigit() and len(symbol) == 6):
        raise InvalidSymbolError(f"无效股票代码：{symbol}")
    if symbol == "999999":
        raise ApiError("行情服务暂时不可用")
    return 1688.0


for symbol in ["600519", "ABC", "999999"]:
    try:
        print(symbol, fetch_price(symbol))
    except InvalidSymbolError as error:
        print("请修改输入：", error)
    except ApiError as error:
        print("稍后重试：", error)


def convert(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as error:
        # from error 保留异常因果链，调试时既能看到业务异常，也能看到原始原因。
        raise InvalidSymbolError("代码必须是数字") from error


try:
    convert("ABC")
except InvalidSymbolError as error:
    print(error)

"""
练习：定义 InsufficientBalanceError，并在余额小于订单金额时抛出。

# ==========================
# 参考答案
# ==========================
class InsufficientBalanceError(RuntimeError):
    pass

def pay(balance: float, amount: float) -> float:
    if amount > balance:
        raise InsufficientBalanceError("余额不足")
    return balance - amount

print(pay(100, 30))

本节总结：raise 主动报告无法继续的情况；自定义异常让调用者精确处理业务错误。
"""
