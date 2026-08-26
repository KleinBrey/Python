from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes import router
from backend.app.services import Service


class FakeIwencaiProvider:
    def __init__(self):
        self.fetch_count = 0

    def fetch_hot_rank(self) -> pd.DataFrame:
        self.fetch_count += 1
        return pd.DataFrame(
            [
                {
                    "symbol": "000001.SZ",
                    "name": "平安银行",
                    "price": "11.20",
                    "change_pct": "-0.50%",
                    "hot_rank": "99",
                }
            ]
        )


class FakeStockHotRepository:
    def __init__(self, latest_update_time: datetime | None):
        self.latest_update_time = latest_update_time
        self.rows = pd.DataFrame(
            [
                {
                    "trade_date": pd.Timestamp("2026-08-26"),
                    "symbol": "000001",
                    "name": "平安银行",
                    "price": 11.2,
                    "change_pct": -0.5,
                    "hot_value": 99.0,
                    "source": "Iwencai",
                    "update_time": pd.Timestamp("2026-08-26 10:00:00"),
                }
            ]
        )
        self.upsert_count = 0

    def get_latest_update_time(self) -> datetime | None:
        return self.latest_update_time

    def get_latest(self) -> pd.DataFrame:
        return self.rows.copy()

    def upsert_stock_hot_daily(self, rows: pd.DataFrame) -> int:
        self.upsert_count += 1
        return len(rows)


@pytest.mark.parametrize(
    ("age", "expected_sync_count"),
    [
        (timedelta(hours=1, minutes=59), 0),
        (timedelta(hours=2), 1),
        (timedelta(hours=3), 1),
    ],
)
def test_get_hot_stock_syncs_only_when_cache_is_two_hours_old_or_older(
    age,
    expected_sync_count,
):
    request_time = datetime(2026, 8, 26, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    repository = FakeStockHotRepository(
        request_time.replace(tzinfo=None) - age,
    )
    provider = FakeIwencaiProvider()
    service = Service(
        iwencai_provider=provider,
        stock_hot_repository=repository,
    )

    result = service.get_hot_stock(request_time)

    assert result["symbol"].tolist() == ["000001"]
    assert provider.fetch_count == expected_sync_count
    assert repository.upsert_count == expected_sync_count


def test_get_hot_stock_syncs_when_database_is_empty():
    repository = FakeStockHotRepository(None)
    provider = FakeIwencaiProvider()
    service = Service(
        iwencai_provider=provider,
        stock_hot_repository=repository,
    )

    service.get_hot_stock(
        datetime(2026, 8, 26, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    )

    assert provider.fetch_count == 1
    assert repository.upsert_count == 1


def test_hot_stock_endpoint_returns_service_data():
    class FakeService:
        def get_hot_stock(self) -> pd.DataFrame:
            return FakeStockHotRepository(None).get_latest()

    app = FastAPI()
    app.include_router(router)
    app.state.service = FakeService()
    client = TestClient(app)

    response = client.get("/hot-stock")

    assert response.status_code == 200
    assert response.json() == [
        {
            "trade_date": "2026-08-26",
            "symbol": "000001",
            "name": "平安银行",
            "price": 11.2,
            "change_pct": -0.5,
            "hot_value": 99.0,
            "source": "Iwencai",
            "update_time": "2026-08-26T10:00:00",
        }
    ]
