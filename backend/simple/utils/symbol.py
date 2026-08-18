import re


def validate_symbol(value: object) -> str:
    """验证股票代码合法性，600519.SH -> 600519"""
    # 输入 600519.SH -> 600519

    symbol = str(value).strip().upper().split(".", maxsplit=1)[0]

    if not re.fullmatch(r"\d{6}", symbol):
        raise ValueError(f"无法识别股票代码: {value!r}")

    return symbol


def exchange_for(code: str) -> str:
    """根据 A 股代码判断所属交易所。"""

    if code.startswith(("4", "8", "92")):
        return "BJ"
    if code.startswith(("5", "6", "9")):
        return "SH"
    return "SZ"
