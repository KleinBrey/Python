"""兼容入口；历史行情已统一到同花顺扶摇官方接口。"""

from data.providers.hithink_financial import fetch_stock_history

__all__ = ["fetch_stock_history"]
