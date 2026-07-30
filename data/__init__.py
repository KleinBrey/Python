"""统一数据接入层。

外部数据源负责获取原始数据，本包负责把它们转换为量化系统的稳定格式。
策略、回测和存储层不应直接依赖某个供应商的字段名。
"""

from data.normalizers import (
    canonical_bars_to_system,
    canonical_stocks_to_system,
    normalize_market_bars,
    normalize_stock_master,
)
from data.registry import get_source, list_sources
from data.service import OFFICIAL_SOURCE, fetch_daily_bars, fetch_stock_master
from data.schemas import BAR_COLUMNS, STOCK_COLUMNS, DataSchemaError

__all__ = [
    "BAR_COLUMNS",
    "STOCK_COLUMNS",
    "DataSchemaError",
    "OFFICIAL_SOURCE",
    "canonical_bars_to_system",
    "canonical_stocks_to_system",
    "fetch_daily_bars",
    "fetch_stock_master",
    "get_source",
    "list_sources",
    "normalize_market_bars",
    "normalize_stock_master",
]
