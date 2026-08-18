"""放量上涨热度选股策略。

策略只负责计算和筛选，不直接请求数据源。股票快照需要包含总市值与
个股热度，日线数据使用 simple.daily_bars 的字段格式。
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


STOCK_COLUMNS = ["symbol", "name", "exchange", "market_cap", "heat"]
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


def _require_columns(
    frame: pd.DataFrame,
    required_columns: list[str],
    frame_name: str,
) -> None:
    missing_columns = [
        column for column in required_columns if column not in frame.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"{frame_name} 缺少字段：{missing_text}")


def _stock_code(value: object) -> str:
    """统一股票代码，同时兼容 600519 和 600519.SH。"""

    return str(value).strip().upper().split(".", maxsplit=1)[0]


@dataclass(frozen=True, slots=True)
class HotVolumeBreakoutConfig:
    """放量上涨热度策略参数。"""

    min_market_cap: float = 10_000_000_000
    recent_volume_days: int = 5
    previous_volume_days: int = 20
    min_volume_ratio: float = 1.5
    min_return_5d_pct: float = 5.0

    @property
    def required_trading_days(self) -> int:
        return self.recent_volume_days + self.previous_volume_days


class HotVolumeBreakoutStrategy:
    """
    筛选市值较大、近 5 日放量上涨且热度较高的 A 股。

    ``stocks`` 字段：
    - symbol: 六位股票代码，可带交易所后缀
    - name: 股票名称
    - exchange: SH、SZ 或 BJ
    - market_cap: 总市值，单位为元
    - heat: 个股热度分数，数值越大越热

    ``daily_bars`` 字段：symbol、date、close、volume。
    """

    def __init__(self, config: HotVolumeBreakoutConfig | None = None):
        self.config = config or HotVolumeBreakoutConfig()

    def select(
        self,
        stocks: pd.DataFrame,
        daily_bars: pd.DataFrame,
    ) -> pd.DataFrame:
        """返回符合条件的股票，按个股热度从高到低排序。"""

        _require_columns(stocks, STOCK_COLUMNS, "stocks")
        _require_columns(daily_bars, DAILY_BAR_COLUMNS, "daily_bars")

        if stocks.empty or daily_bars.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        candidates = stocks[STOCK_COLUMNS].copy()
        candidates["symbol"] = candidates["symbol"].map(_stock_code)
        candidates["exchange"] = candidates["exchange"].astype(str).str.upper()
        candidates["market_cap"] = pd.to_numeric(
            candidates["market_cap"], errors="coerce"
        )
        candidates["heat"] = pd.to_numeric(candidates["heat"], errors="coerce")

        names = candidates["name"].fillna("").astype(str).str.upper()
        is_st = names.str.contains("ST", regex=False)
        is_star_market = candidates["symbol"].str.startswith(("688", "689"))
        is_beijing = (candidates["exchange"] == "BJ") | candidates[
            "symbol"
        ].str.startswith(("4", "8", "92"))

        candidates = candidates.loc[
            (candidates["market_cap"] > self.config.min_market_cap)
            & candidates["heat"].notna()
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
        bars = bars.loc[(bars["close"] > 0) & (bars["volume"] >= 0)]
        bars = bars.loc[bars["symbol"].isin(candidates["symbol"])]

        indicators = self._calculate_indicators(bars)
        if indicators.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        result = candidates.merge(indicators, on="symbol", how="inner")
        # 消除 5% 可能被浮点表示为 5.000000000000004 的边界误差。
        comparable_return = result["return_5d_pct"].round(10)
        result = result.loc[
            (result["volume_ratio"] >= self.config.min_volume_ratio)
            & (comparable_return > self.config.min_return_5d_pct)
        ]

        return (
            result[RESULT_COLUMNS]
            .sort_values(["heat", "symbol"], ascending=[False, True])
            .reset_index(drop=True)
        )

    def _calculate_indicators(self, bars: pd.DataFrame) -> pd.DataFrame:
        """按股票计算 5/20 日均量比和最近 5 个交易日涨幅。"""

        rows: list[dict] = []
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
