from datetime import date, timedelta

import pandas as pd

from backend.app.strategy import HotVolumeBreakoutStrategy


def _bars(
    symbol: str,
    *,
    previous_volume: float = 100,
    recent_volume: float = 150,
    return_pct: float = 6,
    days: int = 25,
) -> pd.DataFrame:
    dates = [date(2026, 7, 1) + timedelta(days=index) for index in range(days)]
    previous_days = max(days - 5, 0)
    volumes = [previous_volume] * previous_days + [recent_volume] * min(days, 5)
    closes = [10.0] * days
    if days >= 5:
        closes[-1] = 10 * (1 + return_pct / 100)
    return pd.DataFrame(
        {
            "symbol": symbol,
            "date": dates,
            "close": closes,
            "volume": volumes,
        }
    )


def test_select_applies_filters_and_sorts_by_heat_descending():
    stocks = pd.DataFrame(
        [
            ["600001", "高热度", "SH", "主板", 20_000_000_000],
            ["300001", "低热度", "SZ", "创业板", 20_000_000_000],
            ["600002", "ST示例", "SH", "主板", 20_000_000_000],
            ["688001", "科创示例", "SH", "科创板", 20_000_000_000],
            ["920001", "北交示例", "BJ", "北交所", 20_000_000_000],
            ["600003", "市值临界", "SH", "主板", 10_000_000_000],
            ["600004", "量比不足", "SH", "主板", 20_000_000_000],
            ["600005", "涨幅不足", "SH", "主板", 20_000_000_000],
        ],
        columns=["symbol", "name", "exchange", "market", "market_cap"],
    )
    daily_bars = pd.concat(
        [
            _bars("600001"),
            _bars("300001"),
            _bars("600002"),
            _bars("688001"),
            _bars("920001"),
            _bars("600003"),
            _bars("600004", recent_volume=149),
            _bars("600005", return_pct=5),
        ],
        ignore_index=True,
    )

    hot_stocks = pd.DataFrame({"symbol": ["600001", "300001"]})
    strategy = HotVolumeBreakoutStrategy()
    strategy._prepare_candidates = lambda stocks, daily_bars: stocks
    result = strategy.select(stocks, daily_bars, hot_stocks)

    assert result["symbol"].tolist() == ["600001", "300001"]
    assert result["volume_ratio"].tolist() == [1.5, 1.5]
    assert result["return_5d_pct"].round(6).tolist() == [6.0, 6.0]


def test_select_skips_stock_with_fewer_than_25_trading_days():
    stocks = pd.DataFrame(
        [["600001", "数据不足", "SH", "主板", 20_000_000_000]],
        columns=["symbol", "name", "exchange", "market", "market_cap"],
    )

    strategy = HotVolumeBreakoutStrategy()
    strategy._prepare_candidates = lambda stocks, daily_bars: stocks
    result = strategy.select(
        stocks,
        _bars("600001", days=24),
        pd.DataFrame({"symbol": ["600001"]}),
    )

    assert result.empty
    assert "volume_ratio" in result.columns
    assert "return_5d_pct" in result.columns
