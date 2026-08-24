"""
总市值大于100亿,ST股除外,科创板除外,北交所除外，
最近5个交易日均成交量/最近5个交易日前20个交易日均成交量大于等于1.5,
最近5日涨幅大于5%,按现在个股热度排序

"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from rich.console import Console

from datetime import date

from backend.app.database import DuckDBDatabase
from backend.app.provider import TushareProvider
from backend.app.repository import (
    DailyBarRepository,
    StockRepository,
    StockHotDailyRepository,
)
from backend.app.utils.symbol import validate_symbol

console = Console()

STOCK_COLUMNS = ["symbol", "name", "exchange", "market", "market_cap"]

DAILY_BAR_COLUMNS = ["symbol", "date", "close", "volume"]

RESULT_COLUMNS = [
    "symbol",
    "name",
    "exchange",
    "market_cap",
    "latest_date",
    "latest_close",
    "recent_5d_avg_volume",
    "previous_20d_avg_volume",
    "volume_ratio",
    "return_5d_pct",
]

INDICATOR_COLUMNS = [
    "symbol",
    "latest_date",
    "latest_close",
    "recent_5d_avg_volume",
    "previous_20d_avg_volume",
    "volume_ratio",
    "return_5d_pct",
]


def select_from_database() -> pd.DataFrame:
    """读取本地数据"""

    database = DuckDBDatabase()

    stocks = StockRepository(database).get_table_data()

    daily_bars = DailyBarRepository(database).get_table_data()

    # 今日日期
    today = date.today().strftime("%Y-%m-%d")

    # 数据库最新交易日
    latest_trade_date = pd.to_datetime(daily_bars["date"]).max().strftime("%Y%m%d")

    console.rule(
        f"最新交易日:{pd.to_datetime(daily_bars["date"]).max().strftime("%Y-%m-%d")}\n今日:{today}"
    )

    hot_stocks = StockHotDailyRepository(database).get_by_trade_date(today)

    if stocks.empty or daily_bars.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    return HotVolumeBreakoutStrategy().select(stocks, daily_bars, hot_stocks)


@dataclass(frozen=True, slots=True)
class HotVolumeBreakoutConfig:
    """策略参数"""

    # 最小市值 100亿
    min_market_cap: float = 10_000_000_000
    # 最近5天的成交量
    recent_volume_days: int = 5
    # 前20天的成交量
    previous_volume_days: int = 20
    # 最近5个交易日均成交量/最近5个交易日前20个交易日均成交量大于等于1.5
    min_volume_ratio: float = 1.5
    # 最近5日涨幅大于5%
    min_return_5d_pct: float = 5.0

    @property
    def required_trading_days(self) -> int:
        """请求交易天数"""
        return self.recent_volume_days + self.previous_volume_days


class HotVolumeBreakoutStrategy:

    def __init__(self, config: HotVolumeBreakoutConfig | None = None):
        self.config = config or HotVolumeBreakoutConfig()

    def select(
        self, stocks: pd.DataFrame, daily_bars: pd.DataFrame, hot_stocks: pd.DataFrame
    ) -> pd.DataFrame:
        """计算指标并返回符合全部条件的股票。"""

        if stocks.empty or daily_bars.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        # 候选池
        candidates = self._prepare_candidates(stocks, daily_bars)

        candidates = self._exclude_special_stocks(candidates)

        candidates = self._filter_market_cap(candidates)

        # 指标计算池
        bars = self._prepare_bars(daily_bars, candidates["symbol"])
        indicators = self._calculate_indicators(bars)

        # 筛选过滤排序
        result = candidates.merge(indicators, on="symbol", how="inner")
        result = self._filter_volume_ratio(result)
        result = self._filter_return(result)
        return self._sort_filter_by_hot(result, hot_stocks)

    @staticmethod
    def _prepare_candidates(
        stocks: pd.DataFrame, daily_bars: pd.DataFrame
    ) -> pd.DataFrame:
        """整理股票字段，并补齐可选字段。"""

        # 最新交易日
        latest_trade_date = pd.to_datetime(daily_bars["date"]).max().strftime("%Y%m%d")

        daily_basic = TushareProvider().fetch_daily_basic(latest_trade_date)

        # 合并股票动态字段
        stocks = stocks.merge(daily_basic, on="symbol", how="left")

        return stocks

    @staticmethod
    def _exclude_special_stocks(candidates: pd.DataFrame) -> pd.DataFrame:
        """排除 ST、科创板和北交所股票。"""

        names = candidates["name"].fillna("").astype(str).str.upper()
        markets = candidates["market"].fillna("").astype(str)
        is_st = names.str.contains("ST", regex=False)
        is_star_market = markets.eq("科创板") | candidates["symbol"].str.startswith(
            ("688", "689")
        )
        is_beijing = (candidates["exchange"] == "BJ") | candidates[
            "symbol"
        ].str.startswith(("4", "8", "92"))

        return candidates.loc[~is_st & ~is_star_market & ~is_beijing]

    def _filter_market_cap(self, candidates: pd.DataFrame) -> pd.DataFrame:
        """保留总市值大于配置阈值的股票。"""

        return candidates.loc[candidates["market_cap"] > self.config.min_market_cap]

    @staticmethod
    def _prepare_bars(
        daily_bars: pd.DataFrame,
        symbols: pd.Series,
    ) -> pd.DataFrame:
        """整理行情字段，并只保留候选股票的有效行情。"""

        bars = daily_bars[DAILY_BAR_COLUMNS].copy()
        bars["symbol"] = bars["symbol"].map(validate_symbol)
        bars["date"] = pd.to_datetime(bars["date"], errors="coerce")
        bars["close"] = pd.to_numeric(bars["close"], errors="coerce")
        bars["volume"] = pd.to_numeric(bars["volume"], errors="coerce")
        bars = bars.dropna(subset=["date", "close", "volume"])
        bars = bars.loc[(bars["close"] > 0) & (bars["volume"] > 0)]
        return bars.loc[bars["symbol"].isin(symbols)]

    def _calculate_indicators(self, bars: pd.DataFrame) -> pd.DataFrame:
        """按股票计算最近 5 日/此前 20 日均量比和 5 日涨幅。"""

        rows: list[dict[str, object]] = []
        required_days = self.config.required_trading_days
        recent_days = self.config.recent_volume_days

        for symbol, symbol_bars in bars.groupby("symbol", sort=False):
            window = (
                symbol_bars.sort_values("date")
                .drop_duplicates(subset="date", keep="last")
                .tail(required_days)
            )
            if len(window) < required_days:
                continue

            previous = window.iloc[:-recent_days]
            recent = window.iloc[-recent_days:]
            previous_avg_volume = previous["volume"].mean()
            if previous_avg_volume <= 0:
                continue

            recent_avg_volume = recent["volume"].mean()
            base_close = previous.iloc[-1]["close"]
            latest = recent.iloc[-1]

            rows.append(
                {
                    "symbol": symbol,
                    "latest_date": latest["date"].date(),
                    "latest_close": latest["close"],
                    "recent_5d_avg_volume": recent_avg_volume,
                    "previous_20d_avg_volume": previous_avg_volume,
                    "volume_ratio": recent_avg_volume / previous_avg_volume,
                    "return_5d_pct": (latest["close"] / base_close - 1) * 100,
                }
            )

        return pd.DataFrame(rows, columns=INDICATOR_COLUMNS)

    def _filter_volume_ratio(self, result: pd.DataFrame) -> pd.DataFrame:
        """保留最近 5 日均量至少是此前 20 日均量 1.5 倍的股票。"""

        return result.loc[result["volume_ratio"] >= self.config.min_volume_ratio]

    def _filter_return(self, result: pd.DataFrame) -> pd.DataFrame:
        """保留最近 5 日涨幅大于 5% 的股票"""

        comparable_return = result["return_5d_pct"].round(10)
        return result.loc[comparable_return > self.config.min_return_5d_pct]

    @staticmethod
    def _sort_filter_by_hot(
        result: pd.DataFrame, hot_stocks: pd.DataFrame
    ) -> pd.DataFrame:
        """按热度进行筛选和排序"""

        # 获取hot_stocks排序
        symbol_order = {
            symbol: index for index, symbol in enumerate(hot_stocks["symbol"])
        }

        # 数字小的靠前
        result["order"] = result["symbol"].map(symbol_order)

        return (
            result[result["order"].notna()].sort_values("order").reset_index(drop=True)
        )


if __name__ == "__main__":
    with console.status("[bold green]正在请求股票数据..."):
        selected_stocks = select_from_database()
    console.print("[green]✓ 请求完成[/green]")
    if selected_stocks.empty:
        print("没有股票符合策略条件")
    else:
        # 不显示整列为空的可选字段（例如当前数据没有 heat）。
        display = selected_stocks.dropna(axis="columns", how="all")
        console.print(
            display[["symbol", "name", "market", "type", "order"]].rename(
                columns={
                    "symbol": "股票代码",
                    "name": "股票名称",
                    "market": "市场",
                    "type": "类型",
                    "order": "热度排名",
                }
            )
        )
        print(f"\n共筛选出 {len(display)} 只股票")
