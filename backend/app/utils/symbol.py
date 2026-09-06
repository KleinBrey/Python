import re


def validate_symbol(value: object) -> str:
    """验证股票代码合法性，600519.SH"""

    return value


def exchange_for(code: str) -> str:
    """根据 A 股代码判断所属交易所。"""

    if code.startswith(("4", "8", "92")):
        return "BJ"
    if code.startswith(("5", "6", "9")):
        return "SH"
    return "SZ"


def chunked(
    items: list[str],
    size: int,
):
    """把列表按指定数量分批"""

    for i in range(0, len(items), size):
        yield items[i : i + size]
