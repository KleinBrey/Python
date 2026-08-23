from datetime import date

import pandas as pd
import pytest

from backend.app.database import DuckDBDatabase
from backend.app.repository import StockHotDailyRepository


@pytest.fixture
def repository(tmp_path) -> StockHotDailyRepository:
    database = DuckDBDatabase()
    database.database_path = tmp_path / "market.duckdb"
    database.initialize()
    return StockHotDailyRepository(database)


def test_upsert_and_get_by_trade_date(repository: StockHotDailyRepository):
    rows = pd.DataFrame(
        [
            ["20260820", "600000", "浦发银行", 12.1, 1.2, 88],
            ["20260820", "000001", "平安银行", 11.2, -0.5, 99],
            # 同一批数据出现重复键时保留最后一条。
            ["20260820", "600000", "浦发银行", 12.2, 1.3, 90],
            ["20260819", "300750", "宁德时代", 200.0, 2.0, 100],
        ],
        columns=[
            "trade_date",
            "symbol",
            "name",
            "price",
            "change_pct",
            "hot_value",
        ],
    )

    affected_rows = repository.upsert_stock_hot_daily(rows)
    result = repository.get_by_trade_date("20260820")

    assert affected_rows == 3
    assert result["symbol"].tolist() == ["000001", "600000"]
    assert result["hot_value"].tolist() == [99.0, 90.0]
    assert result["trade_date"].tolist() == [pd.Timestamp("2026-08-20")] * 2
    assert result["source"].tolist() == ["Iwencai", "Iwencai"]


def test_upsert_updates_existing_trade_date_and_symbol(
    repository: StockHotDailyRepository,
):
    original = pd.DataFrame(
        [["2026-08-20", "600000", "旧名称", 10, 1, 80, "Iwencai"]],
        columns=[
            "trade_date",
            "symbol",
            "name",
            "price",
            "change_pct",
            "hot_value",
            "source",
        ],
    )
    updated = pd.DataFrame(
        [["2026-08-20", "600000", "浦发银行", 12, 2, 95, "Iwencai"]],
        columns=original.columns,
    )

    repository.upsert_stock_hot_daily(original)
    repository.upsert_stock_hot_daily(updated)
    result = repository.get_by_trade_date(date(2026, 8, 20))

    assert len(result) == 1
    assert result.iloc[0]["name"] == "浦发银行"
    assert result.iloc[0]["price"] == 12
    assert result.iloc[0]["hot_value"] == 95


def test_upsert_rejects_missing_columns(repository: StockHotDailyRepository):
    with pytest.raises(ValueError, match="hot_value"):
        repository.upsert_stock_hot_daily(
            pd.DataFrame(
                [{"trade_date": "20260820", "symbol": "600000", "name": "浦发银行"}]
            )
        )
