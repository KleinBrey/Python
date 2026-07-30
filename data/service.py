"""业务层唯一的数据读取门面。"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from data.providers import hithink_financial
from data.schemas import BAR_COLUMNS, empty_frame
from data.storage import write_processed_csv


OFFICIAL_SOURCE = hithink_financial.SOURCE_ID


def _symbol_list(symbols: str | Iterable[str]) -> list[str]:
    raw_values = symbols.split(",") if isinstance(symbols, str) else symbols
    return list(dict.fromkeys(str(item).strip() for item in raw_values if str(item).strip()))


def fetch_daily_bars(
    source: str,
    symbols: str | Iterable[str],
    start_date: str,
    end_date: str,
    *,
    adjustment: str = "none",
    persist: bool = False,
) -> pd.DataFrame:
    """从同花顺扶摇获取一个或多个标的，并返回统一日线格式。"""

    if source != OFFICIAL_SOURCE:
        raise KeyError(
            f"不支持的数据源 {source!r}；结构化行情已统一为 {OFFICIAL_SOURCE!r}"
        )

    frames = [
        hithink_financial.fetch_daily_bars(
            symbol,
            start_date,
            end_date,
            adjustment=adjustment,
        )
        for symbol in _symbol_list(symbols)
    ]
    frames = [frame for frame in frames if not frame.empty]
    frame = pd.concat(frames, ignore_index=True) if frames else empty_frame(BAR_COLUMNS)
    if persist:
        write_processed_csv(OFFICIAL_SOURCE, "daily_bars_latest", frame)
    return frame


def fetch_stock_master(
    source: str = OFFICIAL_SOURCE,
    *,
    include_valuations: bool = True,
    persist: bool = False,
) -> pd.DataFrame:
    """获取扶摇 A 股代码表，并可合并官方最新估值快照。"""

    if source != OFFICIAL_SOURCE:
        raise KeyError(
            f"不支持的数据源 {source!r}；股票主数据已统一为 {OFFICIAL_SOURCE!r}"
        )
    frame = hithink_financial.fetch_stock_master(include_valuations=include_valuations)
    if persist:
        write_processed_csv(OFFICIAL_SOURCE, "stock_master_latest", frame)
    return frame


__all__ = ["OFFICIAL_SOURCE", "fetch_daily_bars", "fetch_stock_master"]
