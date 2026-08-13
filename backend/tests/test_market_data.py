from datetime import date, datetime

import pandas as pd

from backend.app.database import DuckDBDatabase
from backend.app.providers.base import MarketDataProvider
from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


class FakeProvider(MarketDataProvider):
    source_id = "fake"

    def __init__(self):
        self.requests: list[tuple[str, str, str]] = []

    def is_configured(self) -> bool:
        return True

    def list_stocks(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"symbol": "000001.SZ", "code": "000001", "exchange": "SZ", "name": "平安银行", "asset_type": "a-share", "source": "fake"},
                {"symbol": "600519.SH", "code": "600519", "exchange": "SH", "name": "贵州茅台", "asset_type": "a-share", "source": "fake"},
            ]
        )

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self.requests.append((symbol, start_date, end_date))
        return pd.DataFrame(
            [
                {
                    "symbol": symbol,
                    "trade_date": "2026-08-12",
                    "open": 10.0,
                    "high": 10.8,
                    "low": 9.8,
                    "close": 10.5,
                    "pre_close": 10.0,
                    "change": 0.5,
                    "pct_change": 5.0,
                    "volume": 1000.0,
                    "amount": 10_500.0,
                    "adjustment": "none",
                    "source": "fake",
                    "ingested_at": datetime(2026, 8, 12, 18, 0),
                }
            ]
        )


def repository(tmp_path) -> MarketDataRepository:
    database = DuckDBDatabase(tmp_path / "market.duckdb")
    database.initialize()
    return MarketDataRepository(database)


def test_initial_sync_is_idempotent(tmp_path):
    repo = repository(tmp_path)
    service = MarketDataService(repo, FakeProvider(), workers=2)

    assert service.sync("initial", end_date=date(2026, 8, 13))["status"] == "success"
    assert service.sync("initial", end_date=date(2026, 8, 13))["status"] == "success"

    status = repo.status()
    assert status["stock_count"] == 2
    assert status["bar_count"] == 2


def test_daily_sync_rechecks_recent_window(tmp_path):
    repo = repository(tmp_path)
    provider = FakeProvider()
    service = MarketDataService(repo, provider, workers=1)
    service.sync("initial", symbols=["000001"], end_date=date(2026, 8, 13))
    provider.requests.clear()

    service.sync("daily", symbols=["000001"], end_date=date(2026, 8, 13))

    assert provider.requests == [("000001.SZ", "20260807", "20260813")]
    assert len(repo.get_bars("000001.SZ", None, None, 100)) == 1

