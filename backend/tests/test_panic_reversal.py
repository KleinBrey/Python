from __future__ import annotations

import unittest

import pandas as pd

from backend.app.strategy.implementations.panic_reversal import (
    RESULT_COLUMNS,
)
from backend.app.strategy.registry import execute_strategy
from backend.app.strategy.result import format_strategy_result


class FakeTushareProvider:
    def fetch_daily_basic(self, trade_date: str) -> pd.DataFrame:
        return pd.DataFrame(
            {"symbol": ["TEST.SZ"], "market_cap": [20_000_000_000]}
        )


class PanicReversalStrategyTests(unittest.TestCase):
    def test_returns_latest_confirmed_signal(self) -> None:
        closes = [100.0] * 20 + [96.0, 92.0, 88.0, 80.0, 90.0, 95.0]
        daily_bars = pd.DataFrame(
            {
                "symbol": "TEST.SZ",
                "trade_date": pd.date_range("2026-07-01", periods=26),
                "open": [100.0] * 20
                + [100.0, 96.0, 92.0, 88.0, 80.0, 90.0],
                "high": [101.0] * 20
                + [101.0, 97.0, 93.0, 89.0, 91.0, 96.0],
                "low": [99.0] * 20 + [95.0, 91.0, 87.0, 79.0, 78.0, 89.0],
                "close": closes,
                "volume": [100.0] * 23 + [200.0, 200.0, 150.0],
            }
        )
        stocks = pd.DataFrame(
            {
                "symbol": ["TEST.SZ"],
                "name": ["测试股份"],
                "exchange": ["SZ"],
            }
        )
        hot_stocks = pd.DataFrame(
            {"symbol": ["TEST.SZ"], "hot_value": [1000.0]}
        )

        result = execute_strategy(
            "panic-reversal",
            stocks=stocks,
            daily_bars=daily_bars,
            hot_stocks=hot_stocks,
            tushare_provider=FakeTushareProvider(),
        )

        self.assertEqual(result.columns.tolist(), RESULT_COLUMNS)
        self.assertEqual(result["symbol"].tolist(), ["TEST.SZ"])
        self.assertEqual(result.loc[0, "latest_date"], pd.Timestamp("2026-07-26"))
        self.assertTrue(result.loc[0, "confirmed_signal"])
        self.assertEqual(result.loc[0, "signal_stage"], "确认")
        self.assertEqual(result.loc[0, "hot_rank"], 1)

        payload = format_strategy_result("panic-reversal", result, limit=100)
        self.assertEqual(payload["trade_date"], "2026-07-26")
        self.assertEqual(payload["strategy"]["id"], "panic-reversal")


if __name__ == "__main__":
    unittest.main()
