import pandas as pd
import pytest

from backend.app.database import DuckDBDatabase
from backend.app.repository import DailyBarRepository, StockRepository


@pytest.fixture
def database(tmp_path) -> DuckDBDatabase:
    database = DuckDBDatabase()
    database.database_path = tmp_path / "market.duckdb"
    database.initialize()
    return database


def test_stock_upsert_is_idempotent(database: DuckDBDatabase):
    repository = StockRepository(database)
    stocks = pd.DataFrame(
        [
            ["000001", "平安银行", "SZ", "主板", "A股", "test"],
            ["600519", "贵州茅台", "SH", "主板", "A股", "test"],
        ],
        columns=["symbol", "name", "exchange", "market", "type", "source"],
    )

    assert repository.upsert_stocks(stocks) == 2
    assert repository.upsert_stocks(stocks) == 2
    assert repository.get_table_data()["symbol"].tolist() == ["000001", "600519"]


def test_daily_bar_upsert_updates_existing_row(database: DuckDBDatabase):
    repository = DailyBarRepository(database)
    columns = [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "source",
    ]
    original = pd.DataFrame(
        [["600519", "2026-08-21", 10, 11, 9, 10.5, 1000, 10_500, "test"]],
        columns=columns,
    )
    updated = original.copy()
    updated.loc[0, "close"] = 10.8

    assert repository.upsert_daily_bars(original) == 1
    assert repository.upsert_daily_bars(updated) == 1
    result = repository.get_table_data()
    assert len(result) == 1
    assert result.iloc[0]["close"] == 10.8
