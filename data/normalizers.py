"""供应商字段到系统统一字段的转换与清洗。"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Mapping

import pandas as pd

from data.schemas import (
    BAR_COLUMNS,
    STOCK_COLUMNS,
    DataSchemaError,
    empty_frame,
    validate_market_bars,
)


_SYMBOL_PATTERN = re.compile(r"(?:(SH|SZ|BJ)[._-]?)?(\d{6})(?:[._-]?(SH|SZ|BJ))?", re.IGNORECASE)


def _infer_a_share_exchange(code: str) -> str:
    if code.startswith(("4", "8", "92")):
        return "BJ"
    if code.startswith(("5", "6", "9")):
        return "SH"
    if code.startswith(("0", "1", "2", "3")):
        return "SZ"
    return ""


def normalize_symbol(value: object, exchange: object = None) -> tuple[str, str, str]:
    """返回 (完整代码, 纯代码, 交易所)，统一为 600519.SH。"""

    text = str(value or "").strip().upper()
    match = _SYMBOL_PATTERN.search(text)
    if not match:
        raise DataSchemaError(f"无法识别证券代码: {value}")
    prefix_exchange, code, suffix_exchange = match.groups()
    normalized_exchange = str(exchange or "").strip().upper().replace("XSHG", "SH").replace(
        "XSHE", "SZ"
    )
    normalized_exchange = prefix_exchange or suffix_exchange or normalized_exchange
    normalized_exchange = normalized_exchange if normalized_exchange in {"SH", "SZ", "BJ"} else ""
    normalized_exchange = normalized_exchange or _infer_a_share_exchange(code)
    symbol = f"{code}.{normalized_exchange}" if normalized_exchange else code
    return symbol, code, normalized_exchange


def _rename_and_require(
    frame: pd.DataFrame,
    column_map: Mapping[str, str],
    required_targets: set[str],
) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    renamed = frame.rename(columns=dict(column_map)).copy()
    missing = required_targets - set(renamed.columns)
    if missing:
        raise DataSchemaError(f"数据源缺少必要字段: {', '.join(sorted(missing))}")
    return renamed


def _parse_trade_dates(values: pd.Series) -> pd.Series:
    """兼容 YYYYMMDD/带时分秒字符串以及 datetime 对象。"""

    text = values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    parsed = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")
    date_mask = text.str.fullmatch(r"\d{8}", na=False)
    datetime_mask = text.str.fullmatch(r"\d{14}", na=False)
    parsed.loc[date_mask] = pd.to_datetime(text.loc[date_mask], format="%Y%m%d", errors="coerce")
    parsed.loc[datetime_mask] = pd.to_datetime(
        text.loc[datetime_mask],
        format="%Y%m%d%H%M%S",
        errors="coerce",
    )
    other_mask = ~(date_mask | datetime_mask)
    parsed.loc[other_mask] = pd.to_datetime(values.loc[other_mask], errors="coerce")
    return parsed


def normalize_market_bars(
    frame: pd.DataFrame,
    *,
    source: str,
    column_map: Mapping[str, str],
    frequency: str = "1d",
    adjustment: str = "none",
    volume_multiplier: float = 1.0,
    amount_multiplier: float = 1.0,
) -> pd.DataFrame:
    """转换 OHLCV，并统一日期、代码、单位、排序和去重。

    统一单位：成交量为股，成交额为元。
    """

    renamed = _rename_and_require(
        frame,
        column_map,
        {"symbol", "trade_date", "open", "high", "low", "close", "volume"},
    )
    if renamed.empty:
        return empty_frame(BAR_COLUMNS)

    symbol_parts = renamed["symbol"].map(normalize_symbol)
    renamed["symbol"] = symbol_parts.map(lambda item: item[0])
    renamed["code"] = symbol_parts.map(lambda item: item[1])
    renamed["exchange"] = symbol_parts.map(lambda item: item[2])

    if adjustment not in {"none", "qfq", "hfq"}:
        raise DataSchemaError(f"不支持的统一复权类型: {adjustment}")

    parsed_dates = _parse_trade_dates(renamed["trade_date"])
    if parsed_dates.isna().any():
        bad_values = renamed.loc[parsed_dates.isna(), "trade_date"].head(3).tolist()
        raise DataSchemaError(f"存在无法解析的交易日期: {bad_values}")
    date_format = "%Y-%m-%d" if frequency in {"1d", "1w", "1M"} else "%Y-%m-%d %H:%M:%S"
    renamed["trade_date"] = parsed_dates.dt.strftime(date_format)

    numeric_columns = (
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
    )
    for column in numeric_columns:
        if column not in renamed:
            renamed[column] = pd.NA
        renamed[column] = pd.to_numeric(renamed[column], errors="coerce")
    if renamed[["open", "high", "low", "close", "volume"]].isna().any().any():
        raise DataSchemaError("OHLCV 中存在无法转换为数值的字段")

    renamed["volume"] = renamed["volume"] * volume_multiplier
    renamed["amount"] = renamed["amount"] * amount_multiplier
    renamed["frequency"] = frequency
    renamed["adjustment"] = adjustment
    renamed["source"] = source
    renamed["ingested_at"] = datetime.now().astimezone().isoformat(timespec="seconds")

    result = (
        renamed[list(BAR_COLUMNS)]
        .sort_values(["symbol", "trade_date"])
        .drop_duplicates(["symbol", "trade_date", "frequency", "adjustment"], keep="last")
        .reset_index(drop=True)
    )
    validate_market_bars(result)
    return result


def normalize_stock_master(
    frame: pd.DataFrame,
    *,
    source: str,
    column_map: Mapping[str, str],
) -> pd.DataFrame:
    """转换股票基础资料为统一格式。"""

    renamed = _rename_and_require(frame, column_map, {"symbol", "name"})
    if renamed.empty:
        return empty_frame(STOCK_COLUMNS)

    symbol_parts = renamed["symbol"].map(normalize_symbol)
    renamed["symbol"] = symbol_parts.map(lambda item: item[0])
    renamed["code"] = symbol_parts.map(lambda item: item[1])
    renamed["exchange"] = symbol_parts.map(lambda item: item[2])
    for column in ("industry", "list_status", "total_shares", "book_value_per_share", "pb", "market_cap"):
        if column not in renamed:
            renamed[column] = pd.NA
    for column in ("total_shares", "book_value_per_share", "pb", "market_cap"):
        renamed[column] = pd.to_numeric(renamed[column], errors="coerce")
    renamed["source"] = source
    renamed["ingested_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        renamed[list(STOCK_COLUMNS)]
        .drop_duplicates(["symbol"], keep="last")
        .sort_values("symbol")
        .reset_index(drop=True)
    )


def canonical_bars_to_system(frame: pd.DataFrame) -> pd.DataFrame:
    """转换到现有 MongoDB/策略使用的中文列名，保持旧代码兼容。"""

    mapping = {
        "symbol": "股票代码",
        "trade_date": "交易日期",
        "open": "开盘价",
        "high": "最高价",
        "low": "最低价",
        "close": "收盘价",
        "pre_close": "昨收价",
        "change": "涨跌额",
        "pct_change": "涨跌幅",
        "volume": "成交量",
        "amount": "成交额",
        "turnover_rate": "换手率",
        "frequency": "周期",
        "adjustment": "复权类型",
        "source": "数据源",
        "ingested_at": "入库时间",
    }
    return frame.rename(columns=mapping).copy()


def canonical_stocks_to_system(frame: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "symbol": "股票代码",
        "name": "股票名称",
        "industry": "行业",
        "book_value_per_share": "每股净资产",
        "pb": "市净率",
        "total_shares": "总股本(亿)",
        "market_cap": "总市值(亿)",
        "source": "数据源",
        "ingested_at": "入库时间",
    }
    return frame.rename(columns=mapping).copy()
