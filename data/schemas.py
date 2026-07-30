"""项目统一数据层使用的稳定数据契约。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


BAR_COLUMNS = (
    "symbol",
    "code",
    "exchange",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_change",
    "volume",
    "amount",
    "turnover_rate",
    "frequency",
    "adjustment",
    "source",
    "ingested_at",
)

STOCK_COLUMNS = (
    "symbol",
    "code",
    "exchange",
    "name",
    "industry",
    "list_status",
    "total_shares",
    "book_value_per_share",
    "pb",
    "market_cap",
    "source",
    "ingested_at",
)


class DataSchemaError(ValueError):
    """数据源结果无法满足统一格式。"""


@dataclass(frozen=True)
class SourceMetadata:
    source_id: str
    name: str
    kind: str
    credential_env: str | None
    dependency: str | None
    capabilities: tuple[str, ...]
    description: str
    docs_url: str
    local_service: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def empty_frame(columns: tuple[str, ...]) -> pd.DataFrame:
    return pd.DataFrame(columns=list(columns))


def validate_market_bars(frame: pd.DataFrame) -> None:
    """校验会影响回测正确性的核心约束。"""

    missing = {"symbol", "trade_date", "open", "high", "low", "close", "volume", "source"} - set(
        frame.columns
    )
    if missing:
        raise DataSchemaError(f"统一行情缺少字段: {', '.join(sorted(missing))}")
    if frame.empty:
        return
    if frame[["symbol", "trade_date"]].isna().any().any():
        raise DataSchemaError("symbol 和 trade_date 不允许为空")
    if frame.duplicated(["symbol", "trade_date", "frequency", "adjustment"]).any():
        raise DataSchemaError("统一行情存在重复的标的、日期、周期和复权组合")

    invalid_high = frame["high"] < frame[["open", "close", "low"]].max(axis=1)
    invalid_low = frame["low"] > frame[["open", "close", "high"]].min(axis=1)
    if invalid_high.any() or invalid_low.any():
        raise DataSchemaError("行情 OHLC 关系异常：high/low 无法覆盖 open/close")
    if (frame["volume"].dropna() < 0).any():
        raise DataSchemaError("成交量不允许为负数")
