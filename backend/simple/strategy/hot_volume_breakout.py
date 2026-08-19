"""市值、成交量与涨幅组合选股策略。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backend.simple.database import DuckDBDatabase
from backend.simple.provider import TushareProvider
from backend.simple.repository import DailyBarRepository, StockRepository

STOCK_COLUMNS = ["symbol", "name", "exchange", "market_cap"]
DAILY_BAR_COLUMNS = ["symbol", "date", "close", "volume"]
RESULT_COLUMNS = [
    "symbol",
    "name",
    "exchange",
    "market_cap",
    "heat",
    "latest_date",
    "latest_close",
    "recent_5d_avg_volume",
    "previous_20d_avg_volume",
    "volume_ratio",
    "return_5d_pct",
]


def select_from_database() -> pd.DataFrame:
    """读取本地行情，并用最新交易日总市值执行策略。"""

    database = DuckDBDatabase()
    stocks = StockRepository(database).get_table_data()
    daily_bars = DailyBarRepository(database).get_table_data()

    if stocks.empty or daily_bars.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    latest_trade_date = pd.to_datetime(daily_bars["date"]).max().strftime("%Y%m%d")
    market_caps = TushareProvider().fetch_market_caps(latest_trade_date)
    stocks = stocks.merge(market_caps, on="symbol", how="left")

    return HotVolumeBreakoutStrategy().select(stocks, daily_bars)


def _stock_code(value: object) -> str:
    """统一股票代码，同时兼容 600519 和 600519.SH。"""

    return str(value).strip().upper().split(".", maxsplit=1)[0]


@dataclass(frozen=True, slots=True)
class HotVolumeBreakoutConfig:
    """策略参数，市值单位为元。"""

    min_market_cap: float = 10_000_000_000
    recent_volume_days: int = 5
    previous_volume_days: int = 20
    min_volume_ratio: float = 1.5
    min_return_5d_pct: float = 5.0

    @property
    def required_trading_days(self) -> int:
        return self.recent_volume_days + self.previous_volume_days


class HotVolumeBreakoutStrategy:
    """筛选大市值、近 5 日放量上涨的非 ST 普通 A 股。"""

    def __init__(self, config: HotVolumeBreakoutConfig | None = None):
        self.config = config or HotVolumeBreakoutConfig()

    def select(
        self,
        stocks: pd.DataFrame,
        daily_bars: pd.DataFrame,
    ) -> pd.DataFrame:
        """计算指标并返回符合全部条件的股票。"""

        if stocks.empty or daily_bars.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        candidate_columns = STOCK_COLUMNS.copy()
        for optional_column in ("market", "heat"):
            if optional_column in stocks.columns:
                candidate_columns.append(optional_column)

        candidates = stocks[candidate_columns].copy()
        if "market" not in candidates.columns:
            candidates["market"] = ""
        if "heat" not in candidates.columns:
            candidates["heat"] = pd.NA

        candidates["symbol"] = candidates["symbol"].map(_stock_code)
        candidates["exchange"] = candidates["exchange"].astype(str).str.upper()
        candidates["market_cap"] = pd.to_numeric(
            candidates["market_cap"], errors="coerce"
        )
        candidates["heat"] = pd.to_numeric(candidates["heat"], errors="coerce")

        names = candidates["name"].fillna("").astype(str).str.upper()
        markets = candidates["market"].fillna("").astype(str)
        is_st = names.str.contains("ST", regex=False)
        is_star_market = markets.eq("科创板") | candidates["symbol"].str.startswith(
            ("688", "689")
        )
        is_beijing = (candidates["exchange"] == "BJ") | candidates[
            "symbol"
        ].str.startswith(("4", "8", "92"))

        candidates = candidates.loc[
            (candidates["market_cap"] > self.config.min_market_cap)
            & ~is_st
            & ~is_star_market
            & ~is_beijing
        ]
        if candidates.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        bars = daily_bars[DAILY_BAR_COLUMNS].copy()
        bars["symbol"] = bars["symbol"].map(_stock_code)
        bars["date"] = pd.to_datetime(bars["date"], errors="coerce")
        bars["close"] = pd.to_numeric(bars["close"], errors="coerce")
        bars["volume"] = pd.to_numeric(bars["volume"], errors="coerce")
        bars = bars.dropna(subset=["date", "close", "volume"])
        bars = bars.loc[(bars["close"] > 0) & (bars["volume"] > 0)]
        bars = bars.loc[bars["symbol"].isin(candidates["symbol"])]

        indicators = self._calculate_indicators(bars)
        if indicators.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        result = candidates.merge(indicators, on="symbol", how="inner")
        comparable_return = result["return_5d_pct"].round(10)
        result = result.loc[
            (result["volume_ratio"] >= self.config.min_volume_ratio)
            & (comparable_return > self.config.min_return_5d_pct)
        ]

        sort_columns = ["volume_ratio", "return_5d_pct", "market_cap", "symbol"]
        ascending = [False, False, False, True]
        if result["heat"].notna().any():
            sort_columns.insert(0, "heat")
            ascending.insert(0, False)

        return (
            result[RESULT_COLUMNS]
            .sort_values(sort_columns, ascending=ascending)
            .reset_index(drop=True)
        )

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

        return pd.DataFrame(rows)


if __name__ == "__main__":
    selected_stocks = select_from_database()
    if selected_stocks.empty:
        print("没有股票符合策略条件")
    else:
        # 不显示整列为空的可选字段（例如当前数据没有 heat）。
        display = selected_stocks.dropna(axis="columns", how="all")
        print(display)
        print(f"\n共筛选出 {len(display)} 只股票")
