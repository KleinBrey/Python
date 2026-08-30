"""六个基础量价因子。

这个文件用于因子学习，只负责把日 K DataFrame 转换成因子 DataFrame，
不做选股、评分或交易。所有 rolling 和 shift 只使用当前及历史数据。

输入至少包含：``symbol/trade_date/close/volume``。
"""

from __future__ import annotations

import pandas as pd

from datetime import date

from backend.app.database import DuckDBDatabase
from backend.app.provider import TushareProvider
from backend.app.repository import (
    DailyBarRepository,
    StockRepository,
    StockHotDailyRepository,
)

REQUIRED_COLUMNS = ["symbol", "trade_date", "close", "volume"]
FACTOR_COLUMNS = [
    "return_1d",
    "momentum_5d",
    "momentum_20d",
    "volume_ratio_5d",
    "volatility_20d",
    "distance_ma20",
]


def calculate_return_1d(df: pd.DataFrame) -> pd.DataFrame:
    """计算单日收益率：今日收盘价 / 昨日收盘价 - 1。"""

    result = df.copy()
    result["return_1d"] = result["close"].pct_change()
    return result


def calculate_momentum_5d(df: pd.DataFrame) -> pd.DataFrame:
    """计算 5 日动量：今日收盘价 / 5 个交易日前收盘价 - 1。"""

    result = df.copy()
    result["momentum_5d"] = result["close"] / result["close"].shift(5) - 1
    return result


def calculate_momentum_20d(df: pd.DataFrame) -> pd.DataFrame:
    """计算 20 日动量：今日收盘价 / 20 个交易日前收盘价 - 1。"""

    result = df.copy()
    result["momentum_20d"] = result["close"] / result["close"].shift(20) - 1
    return result


def calculate_volume_ratio_5d(df: pd.DataFrame) -> pd.DataFrame:
    """计算当日成交量相对最近 5 日平均成交量的倍数。"""

    result = df.copy()
    # 这里的“最近 5 日”包含当日，与图片中的“当前成交量 / 5 日均量”一致。
    volume_ma5 = result["volume"].rolling(5).mean()
    result["volume_ratio_5d"] = result["volume"] / volume_ma5
    return result


def calculate_volatility_20d(df: pd.DataFrame) -> pd.DataFrame:
    """计算最近 20 个单日收益率的标准差，结果为未年化日频波动率。"""

    result = df.copy()
    daily_return = result["close"].pct_change(fill_method=None)
    result["volatility_20d"] = daily_return.rolling(20).std()
    return result


def calculate_distance_ma20(df: pd.DataFrame) -> pd.DataFrame:
    """计算股价偏离 20 日均线的比例：收盘价 / MA20 - 1。"""

    result = df.copy()
    moving_average_20d = result["close"].rolling(20).mean()
    result["distance_ma20"] = result["close"] / moving_average_20d - 1
    return result


def calculate_basic_factors(df: pd.DataFrame) -> pd.DataFrame:
    """按股票计算全部基础因子，返回原始字段和六个因子字段。"""

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"日 K 数据缺少字段：{missing_text}")

    bars = df.copy()
    bars["trade_date"] = pd.to_datetime(bars["trade_date"], errors="raise")
    bars["close"] = pd.to_numeric(bars["close"], errors="raise")
    bars["volume"] = pd.to_numeric(bars["volume"], errors="raise")

    if bars.empty:
        for column in FACTOR_COLUMNS:
            bars[column] = pd.Series(dtype="float64")
        return bars

    results = []
    for _, symbol_bars in bars.groupby("symbol", sort=False, dropna=False):
        # 每只股票先按日期排列，所有 shift/rolling 都不会跨股票计算。
        result = symbol_bars.sort_values("trade_date").copy()
        result = calculate_return_1d(result)
        result = calculate_momentum_5d(result)
        result = calculate_momentum_20d(result)
        result = calculate_volume_ratio_5d(result)
        result = calculate_volatility_20d(result)
        result = calculate_distance_ma20(result)
        results.append(result)

    return (
        pd.concat(results).sort_values(["symbol", "trade_date"]).reset_index(drop=True)
    )


if __name__ == "__main__":

    database = DuckDBDatabase()

    stocks = StockRepository(database).get_table_data()

    daily_bars = DailyBarRepository(database).get_table_data()

    # 今日日期
    today = date.today().strftime("%Y-%m-%d")

    # 数据库最新交易日
    latest_trade_date = (
        pd.to_datetime(daily_bars["trade_date"]).max().strftime("%Y%m%d")
    )

    hot_stocks = StockHotDailyRepository(database).get_by_trade_date(today)

    """
    今日收益率
    """
    # 先取最近5天的值
    date_range_list = daily_bars[
        daily_bars["trade_date"].between("2026-08-21", "2026-08-28")
    ].head(50)

    date_range_list = date_range_list.sort_values("trade_date", ascending=False)

    # 开始添加因子
    date_range_list["return_1d"] = date_range_list["close"].pct_change()
    date_range_list["return_1d_2"] = (
        date_range_list["close"] / date_range_list["close"].shift(1) - 1
    )
    date_range_list["momentum_5d"] = (
        date_range_list["close"] / date_range_list["close"].shift(5) - 1
    )

    volume_ma5 = date_range_list["volume"].rolling(5).mean()
    print(volume_ma5)
    date_range_list["volume_ratio_5d"] = date_range_list["volume"] / volume_ma5

    # 只取今日的数据
    # date_range_list = date_range_list[
    #     date_range_list["trade_date"] == "2026-08-28"
    # ].reset_index()

    print(date_range_list)

    # print(
    #     daily_bars.groupby("symbol")
    #     .get_group("600487.SH")
    #     .sort_values(["trade_date"])
    #     .shape
    # )

    # print(stocks, daily_bars, hot_stocks)

    # calculate_basic_factors()
