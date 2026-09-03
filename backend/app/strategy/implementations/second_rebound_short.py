"""二次反弹到前高后的做空信号策略。

策略只识别信号，不执行交易：

    前高 -> 明显回落 -> 第二次反弹到前高 -> 放量拒绝 K 线 -> 下跌跟随

所有判断只使用当前及历史日 K，不使用未来数据。
"""

from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table

from backend.app.database import DuckDBDatabase
from backend.app.provider import TushareProvider
from backend.app.repository import (
    DailyBarRepository,
    StockHotDailyRepository,
    StockRepository,
)

PEAK_LOOKBACK_DAYS = 60
PEAK_MIN_GAP_DAYS = 10
PULLBACK_LOOKBACK_DAYS = 30
MIN_PULLBACK = 0.08
SECOND_PEAK_MIN_RATIO = 0.95
SECOND_PEAK_MAX_RATIO = 1.03

MIN_VOLUME_RATIO = 1.5
MIN_UPPER_WICK_RATIO = 0.30
MIN_BEAR_BODY_RATIO = 0.50
MIN_BEAR_RETURN = -0.025
MAX_REJECTION_CLOSE_POSITION = 0.55
MAX_FOLLOW_CLOSE_POSITION = 0.50

# 本地日 K 来自 Tushare，成交额单位为千元，20 万即 2 亿元。
MIN_AMOUNT = 200_000

REQUIRED_COLUMNS = [
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
]

RESULT_COLUMNS = [
    "symbol",
    "name",
    "exchange",
    "market_cap",
    "latest_date",
    "latest_close",
    "latest_1d_pct",
    "latest_5d_pct",
    "volume_ratio",
    "first_peak",
    "pullback_depth",
    "upper_wick_ratio",
    "bear_body_ratio",
    "signal_stage",
    "hot_rank",
    "hot_value",
]


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算单只股票的前高、二次反弹、拒绝 K 线和跟随信号。"""

    result = df.sort_values("date").copy()
    previous_close = result["close"].shift(1)

    result["return_1d"] = result["close"] / previous_close - 1
    result["return_5d"] = result["close"] / result["close"].shift(5) - 1

    # 前高必须至少出现在 10 个交易日以前，给中间回落和再次反弹留出空间。
    peak_window = PEAK_LOOKBACK_DAYS - PEAK_MIN_GAP_DAYS
    result["first_peak"] = (
        result["high"].shift(PEAK_MIN_GAP_DAYS).rolling(peak_window).max()
    )
    result["pullback_low"] = (
        result["low"].shift(1).rolling(PULLBACK_LOOKBACK_DAYS).min()
    )
    result["pullback_depth"] = result["pullback_low"] / result["first_peak"] - 1

    second_peak_ratio = result["high"] / result["first_peak"]
    result["second_rally"] = (
        (result["pullback_depth"] <= -MIN_PULLBACK)
        & second_peak_ratio.between(SECOND_PEAK_MIN_RATIO, SECOND_PEAK_MAX_RATIO)
    )

    result["volume_ma20"] = result["volume"].shift(1).rolling(20).mean()
    result["volume_ratio"] = result["volume"] / result["volume_ma20"]

    candle_range = result["high"] - result["low"]
    candle_range = candle_range.where(candle_range != 0)
    result["close_position"] = (result["close"] - result["low"]) / candle_range
    result["upper_wick_ratio"] = (
        result["high"] - result[["open", "close"]].max(axis=1)
    ) / candle_range
    result["bear_body_ratio"] = (
        (result["open"] - result["close"]) / candle_range
    ).clip(lower=0)

    result["long_upper_wick"] = (
        (result["upper_wick_ratio"] >= MIN_UPPER_WICK_RATIO)
        & (result["close_position"] <= MAX_REJECTION_CLOSE_POSITION)
    )
    result["big_bear"] = (
        (result["close"] < result["open"])
        & (result["bear_body_ratio"] >= MIN_BEAR_BODY_RATIO)
        & (result["return_1d"] <= MIN_BEAR_RETURN)
    )

    result["rejection_signal"] = (
        result["second_rally"]
        & (result["volume_ratio"] >= MIN_VOLUME_RATIO)
        & (result["long_upper_wick"] | result["big_bear"])
        & (result["amount"] >= MIN_AMOUNT)
    )

    previous_rejection = result["rejection_signal"].shift(1).fillna(False)
    strong_follow = (result["close"] < result["low"].shift(1)) | (
        result["return_1d"] <= -0.02
    )
    result["follow_signal"] = (
        previous_rejection.astype(bool)
        & (result["close"] < result["open"])
        & (result["close"] < previous_close)
        & (result["close_position"] <= MAX_FOLLOW_CLOSE_POSITION)
        & strong_follow
    )
    result["signal"] = result["follow_signal"]

    # 确认日显示前一天拒绝 K 线的指标，更容易判断信号来源。
    for column in [
        "first_peak",
        "pullback_depth",
        "volume_ratio",
        "upper_wick_ratio",
        "bear_body_ratio",
    ]:
        result[f"rejection_{column}"] = result[column].shift(1)

    return result


def run_second_rebound_short_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """按股票分组计算二次冲高做空信号。"""

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df]
    if missing_columns:
        raise ValueError(f"日 K 数据缺少字段：{', '.join(missing_columns)}")

    bars = df.copy()
    bars["date"] = pd.to_datetime(bars["date"], errors="raise")
    for column in ["open", "high", "low", "close", "volume", "amount"]:
        bars[column] = pd.to_numeric(bars[column], errors="raise")

    results = [
        calculate_indicators(symbol_bars)
        for _, symbol_bars in bars.groupby("symbol", sort=False)
    ]
    if not results:
        return bars
    return pd.concat(results).sort_values(["symbol", "date"]).reset_index(drop=True)


def latest_filter_counts(signals: pd.DataFrame) -> list[tuple[str, int]]:
    """统计最新交易日的高位做空筛选漏斗。"""

    latest = signals.groupby("symbol", sort=False).tail(1)
    return [
        ("已有10至60日前高", int(latest["first_peak"].notna().sum())),
        ("回落≥8%后第二次反弹到前高", int(latest["second_rally"].sum())),
        ("高位放量长上影或大阴线", int(latest["rejection_signal"].sum())),
        ("次日继续下跌确认", int(latest["follow_signal"].sum())),
    ]


def latest_confirmed_signals(signals: pd.DataFrame) -> pd.DataFrame:
    """提取最新确认信号，并使用拒绝日的形态指标。"""

    latest = signals.groupby("symbol", sort=False).tail(1).copy()
    latest = latest[latest["follow_signal"]].copy()
    for column in [
        "first_peak",
        "pullback_depth",
        "volume_ratio",
        "upper_wick_ratio",
        "bear_body_ratio",
    ]:
        latest[column] = latest[f"rejection_{column}"]
    return latest


def print_terminal_report(
    signals: pd.DataFrame,
    stocks: pd.DataFrame,
    hot_stocks: pd.DataFrame,
) -> None:
    """用 Rich Table 打印筛选漏斗和高位做空信号。"""

    trade_date = signals["date"].max().date().isoformat()
    funnel_table = Table(title=f"二次冲高做空 · {trade_date}")
    funnel_table.add_column("筛选阶段", style="cyan")
    funnel_table.add_column("股票数量", justify="right", style="bold")
    for condition, count in latest_filter_counts(signals):
        funnel_table.add_row(condition, f"{count} 只")

    console = Console()
    console.print(funnel_table)

    stock_info = stocks[
        ~stocks["name"].str.contains("ST", na=False) & stocks["exchange"].ne("BJ")
    ]
    selected = stock_info.merge(latest_confirmed_signals(signals), on="symbol")

    hot = hot_stocks.drop_duplicates("symbol").reset_index(drop=True).copy()
    hot["hot_rank"] = hot.index + 1
    selected = selected.merge(
        hot[["symbol", "hot_rank"]], on="symbol", how="left"
    ).sort_values(["hot_rank", "return_1d"], na_position="last")

    if selected.empty:
        console.print("[yellow]当前交易日没有高位做空确认信号。[/yellow]")
        return

    result_table = Table(title="高位做空确认信号")
    for column in [
        "股票",
        "代码",
        "收盘价",
        "当日跌幅",
        "前高",
        "中间回落",
        "拒绝日量比",
        "上影占比",
        "阴线实体",
        "热度排名",
    ]:
        result_table.add_column(column, justify="right" if column != "股票" else "left")

    for row in selected.itertuples():
        hot_rank = "-" if pd.isna(row.hot_rank) else str(int(row.hot_rank))
        result_table.add_row(
            row.name,
            row.symbol,
            f"{row.close:.2f}",
            f"{row.return_1d:.2%}",
            f"{row.first_peak:.2f}",
            f"{row.pullback_depth:.2%}",
            f"{row.volume_ratio:.2f}x",
            f"{row.upper_wick_ratio:.2%}",
            f"{row.bear_body_ratio:.2%}",
            hot_rank,
        )
    console.print(result_table)


def run_strategy(
    *,
    stocks: pd.DataFrame,
    daily_bars: pd.DataFrame,
    hot_stocks: pd.DataFrame,
    tushare_provider: TushareProvider,
) -> pd.DataFrame:
    """返回最新交易日得到下跌跟随确认的高位做空信号。"""

    if daily_bars.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    signals = run_second_rebound_short_strategy(
        daily_bars.rename(columns={"trade_date": "date"})
    )
    latest = latest_confirmed_signals(signals).rename(
        columns={
            "date": "latest_date",
            "close": "latest_close",
            "return_1d": "latest_1d_pct",
            "return_5d": "latest_5d_pct",
        }
    )
    if latest.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    latest["signal_stage"] = "跟随确认"
    trade_date = latest["latest_date"].max().strftime("%Y%m%d")
    stock_info = stocks.merge(
        tushare_provider.fetch_daily_basic(trade_date),
        on="symbol",
        how="left",
    )
    stock_info = stock_info[
        ~stock_info["name"].str.contains("ST", na=False)
        & stock_info["exchange"].ne("BJ")
    ]

    hot = hot_stocks.drop_duplicates("symbol").reset_index(drop=True).copy()
    hot["hot_rank"] = hot.index + 1

    return (
        stock_info.merge(latest, on="symbol")
        .merge(hot[["symbol", "hot_rank", "hot_value"]], on="symbol", how="left")
        .sort_values(["hot_rank", "latest_1d_pct"], na_position="last")[
            RESULT_COLUMNS
        ]
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    console = Console()
    with console.status("[bold green]正在读取本地数据并计算策略..."):
        database = DuckDBDatabase()
        stocks = StockRepository(database).get_table_data()
        daily_bars = DailyBarRepository(database).get_table_data()
        hot_stocks = StockHotDailyRepository(database).get_latest()
        signals = run_second_rebound_short_strategy(
            daily_bars.rename(columns={"trade_date": "date"})
        )

    print_terminal_report(signals, stocks, hot_stocks)
