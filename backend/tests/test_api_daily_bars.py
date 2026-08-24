import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes import router
from backend.app.database import DuckDBDatabase
from backend.app.repository import DailyBarRepository


@pytest.fixture
def daily_repository(tmp_path) -> DailyBarRepository:
    """创建独立的临时数据库，避免接口测试读写开发数据库。"""

    database = DuckDBDatabase()
    database.database_path = tmp_path / "market.duckdb"
    database.initialize()

    repository = DailyBarRepository(database)
    rows = pd.DataFrame(
        [
            ["600519", "2026-08-20", 1400, 1420, 1390, 1410, 100, None, "test"],
            ["600519", "2026-08-21", 1410, 1440, 1405, 1430, 120, 171600, "test"],
            ["600519", "2026-08-22", 1430, 1450, 1420, 1440, 110, 158400, "test"],
            ["000001", "2026-08-21", 10, 11, 9.5, 10.5, 200, 2100, "test"],
        ],
        columns=[
            "symbol",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "source",
        ],
    )
    repository.upsert_daily_bars(rows)
    return repository


@pytest.fixture
def client(daily_repository: DailyBarRepository) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.state.daily_repository = daily_repository
    return TestClient(app)


def test_get_daily_bars_filters_symbol_and_inclusive_date_range(client: TestClient):
    response = client.get(
        "/daily-bars",
        params={
            "symbol": "600519.SH",
            "start_date": "2026-08-20",
            "end_date": "2026-08-21",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "symbol": "600519",
            "date": "2026-08-20",
            "open": 1400.0,
            "high": 1420.0,
            "low": 1390.0,
            "close": 1410.0,
            "volume": 100.0,
            "amount": None,
            "source": "test",
        },
        {
            "symbol": "600519",
            "date": "2026-08-21",
            "open": 1410.0,
            "high": 1440.0,
            "low": 1405.0,
            "close": 1430.0,
            "volume": 120.0,
            "amount": 171600.0,
            "source": "test",
        },
    ]


def test_get_daily_bars_returns_empty_list_when_no_data(client: TestClient):
    response = client.get(
        "/daily-bars",
        params={
            "symbol": "300750",
            "start_date": "2026-08-20",
            "end_date": "2026-08-21",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    ("params", "expected_detail"),
    [
        (
            {
                "symbol": "invalid",
                "start_date": "2026-08-20",
                "end_date": "2026-08-21",
            },
            "无法识别股票代码",
        ),
        (
            {
                "symbol": "600519",
                "start_date": "2026-08-22",
                "end_date": "2026-08-20",
            },
            "开始日期不能晚于结束日期",
        ),
    ],
)
def test_get_daily_bars_rejects_invalid_parameters(
    client: TestClient,
    params: dict[str, str],
    expected_detail: str,
):
    response = client.get("/daily-bars", params=params)

    assert response.status_code == 422
    assert expected_detail in response.json()["detail"]
