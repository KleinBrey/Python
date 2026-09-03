"""强势突破后缩量回调，再放量上涨企稳的选股策略。"""

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

PRIOR_HIGH_DAYS = 20
BREAKOUT_DAYS = 5
MIN_BREAKOUT_RETURN = 0.10
MIN_PULLBACK_DAYS = 3
MAX_PULLBACK_DAYS = 20
MAX_PULLBACK_VOLUME_RATIO = 0.80
MAX_PULLBACK_DEPTH = 0.30
MIN_CONFIRM_BODY = 0.02
MIN_CONFIRM_VOLUME_RATIO = 1.30

REQUIRED_COLUMNS = ["symbol", "date", "open", "high", "low", "close", "volume"]

SIGNAL_COLUMNS = [
    "symbol",
    "date",
    "close",
    "return_1d",
    "return_5d",
    "volume_ratio",
    "breakout_return",
    "pullback_depth",
    "pullback_volume_ratio",
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
    "breakout_return",
    "pullback_depth",
    "pullback_volume_ratio",
    "signal_stage",
    "hot_rank",
    "hot_value",
]


def find_latest_signal(bars: pd.DataFrame) -> dict[str, object] | None:
    """判断单只股票的最新交易日是否完成三阶段形态。"""

    latest_index = len(bars) - 1
    if latest_index < PRIOR_HIGH_DAYS + BREAKOUT_DAYS + MIN_PULLBACK_DAYS:
        return None

    latest = bars.iloc[latest_index]
    previous = bars.iloc[latest_index - 1]
    candle_range = latest["high"] - latest["low"]
    close_position = (
        (latest["close"] - latest["low"]) / candle_range
        if candle_range > 0
        else 0
    )
    body_return = latest["close"] / latest["open"] - 1

    # 最新 K 线先满足“中阳线企稳”，再向前寻找对应的突破和回调段。
    if (
        latest["close"] <= previous["close"]
        or body_return < MIN_CONFIRM_BODY
        or close_position < 0.65
    ):
        return None

    first_breakout_end = max(
        PRIOR_HIGH_DAYS + BREAKOUT_DAYS - 1,
        latest_index - MAX_PULLBACK_DAYS - 1,
    )
    last_breakout_end = latest_index - MIN_PULLBACK_DAYS - 1

    for breakout_end in range(last_breakout_end, first_breakout_end - 1, -1):
        breakout_start = breakout_end - BREAKOUT_DAYS + 1
        history = bars.iloc[breakout_start - PRIOR_HIGH_DAYS : breakout_start]
        breakout = bars.iloc[breakout_start : breakout_end + 1]
        pullback = bars.iloc[breakout_end + 1 : latest_index]

        breakout_return = breakout.iloc[-1]["close"] / history.iloc[-1]["close"] - 1
        if (
            breakout_return < MIN_BREAKOUT_RETURN
            or breakout.iloc[-1]["close"] < breakout["close"].max()
            or breakout.iloc[-1]["close"] <= history["high"].max()
        ):
            continue

        breakout_volume = breakout["volume"].mean()
        pullback_volume = pullback["volume"].mean()
        pullback_volume_ratio = pullback_volume / breakout_volume
        pullback_depth = pullback["low"].min() / breakout["high"].max() - 1
        volume_ratio = latest["volume"] / pullback_volume

        if (
            pullback_volume_ratio > MAX_PULLBACK_VOLUME_RATIO
            or pullback_depth < -MAX_PULLBACK_DEPTH
            or volume_ratio < MIN_CONFIRM_VOLUME_RATIO
            or latest["close"] <= pullback["high"].tail(3).max()
        ):
            continue

        return {
            "symbol": latest["symbol"],
            "date": latest["date"],
            "close": latest["close"],
            "return_1d": latest["close"] / previous["close"] - 1,
            "return_5d": latest["close"] / bars.iloc[latest_index - 5]["close"] - 1,
            "volume_ratio": volume_ratio,
            "breakout_return": breakout_return,
            "pullback_depth": pullback_depth,
            "pullback_volume_ratio": pullback_volume_ratio,
        }

    return None


def run_strong_breakout_pullback_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """按股票分组，返回最新交易日形成放量企稳信号的股票。"""

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df]
    if missing_columns:
        raise ValueError(f"日 K 数据缺少字段：{', '.join(missing_columns)}")

    bars = df.copy()
    bars["date"] = pd.to_datetime(bars["date"], errors="raise")
    for column in ["open", "high", "low", "close", "volume"]:
        bars[column] = pd.to_numeric(bars[column], errors="raise")
    bars = bars[(bars["open"] > 0) & (bars["volume"] > 0)]

    signals = []
    for _, symbol_bars in bars.groupby("symbol", sort=False):
        ordered = (
            symbol_bars.sort_values("date")
            .drop_duplicates("date", keep="last")
            .tail(PRIOR_HIGH_DAYS + BREAKOUT_DAYS + MAX_PULLBACK_DAYS + 1)
        )
        signal = find_latest_signal(ordered.reset_index(drop=True))
        if signal:
            signals.append(signal)

    result = pd.DataFrame(signals, columns=SIGNAL_COLUMNS)
    if result.empty:
        return result
    return result[result["date"] == bars["date"].max()].reset_index(drop=True)


def run_strategy(
    *,
    stocks: pd.DataFrame,
    daily_bars: pd.DataFrame,
    hot_stocks: pd.DataFrame,
    tushare_provider: TushareProvider,
) -> pd.DataFrame:
    """供策略接口调用，补齐股票信息并按热度排序。"""

    if daily_bars.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    signals = run_strong_breakout_pullback_strategy(
        daily_bars.rename(columns={"trade_date": "date"})
    ).rename(
        columns={
            "date": "latest_date",
            "close": "latest_close",
            "return_1d": "latest_1d_pct",
            "return_5d": "latest_5d_pct",
        }
    )
    if signals.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    signals["signal_stage"] = "放量企稳"
    trade_date = signals["latest_date"].max().strftime("%Y%m%d")
    stock_info = stocks.merge(
        tushare_provider.fetch_daily_basic(trade_date),
        on="symbol",
        how="left",
    )

    hot = hot_stocks.drop_duplicates("symbol").reset_index(drop=True).copy()
    hot["hot_rank"] = hot.index + 1

    return (
        stock_info.merge(signals, on="symbol")
        .merge(hot[["symbol", "hot_rank", "hot_value"]], on="symbol", how="left")
        .sort_values(
            ["hot_rank", "latest_1d_pct"],
            ascending=[True, False],
            na_position="last",
        )[RESULT_COLUMNS]
        .reset_index(drop=True)
    )


def print_terminal_report(
    signals: pd.DataFrame,
    stocks: pd.DataFrame,
    hot_stocks: pd.DataFrame,
) -> None:
    """用 Rich Table 打印最新选股结果。"""

    console = Console()
    if signals.empty:
        console.print("[yellow]当前交易日没有符合条件的股票。[/yellow]")
        return

    hot = hot_stocks.drop_duplicates("symbol").reset_index(drop=True).copy()
    hot["hot_rank"] = hot.index + 1
    selected = (
        stocks[["symbol", "name"]]
        .merge(signals, on="symbol")
        .merge(hot[["symbol", "hot_rank"]], on="symbol", how="left")
        .sort_values(
            ["hot_rank", "return_1d"],
            ascending=[True, False],
            na_position="last",
        )
    )

    trade_date = signals["date"].max().date().isoformat()
    table = Table(
        title=f"强势突破缩量回调放量企稳 · {trade_date}",
        padding=(0, 0),
    )
    columns = [
        ("股票", "left"),
        ("代码", "left"),
        ("收盘价", "right"),
        ("当日涨幅", "right"),
        ("突破涨幅", "right"),
        ("回调幅度", "right"),
        ("缩量/放量", "right"),
        ("热度排名", "right"),
    ]
    for title, justify in columns:
        table.add_column(title, justify=justify)

    for row in selected.itertuples():
        hot_rank = "-" if pd.isna(row.hot_rank) else str(int(row.hot_rank))
        table.add_row(
            row.name,
            row.symbol,
            f"{row.close:.2f}",
            f"{row.return_1d:.2%}",
            f"{row.breakout_return:.2%}",
            f"{row.pullback_depth:.2%}",
            f"{row.pullback_volume_ratio:.2f}x/{row.volume_ratio:.2f}x",
            hot_rank,
        )

    console.print(table)
    console.print(f"[green]共筛选出 {len(selected)} 只股票。[/green]")


if __name__ == "__main__":
    console = Console()
    with console.status("[bold green]正在读取本地行情并运行策略..."):
        database = DuckDBDatabase()
        stocks = StockRepository(database).get_table_data()
        daily_bars = DailyBarRepository(database).get_table_data()
        hot_stocks = StockHotDailyRepository(database).get_latest()
        signals = run_strong_breakout_pullback_strategy(
            daily_bars.rename(columns={"trade_date": "date"})
        )

    print_terminal_report(signals, stocks, hot_stocks)
