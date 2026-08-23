import pandas as pd

from backend.app.services import Service


class FakeIwencaiProvider:
    def fetch_hot_rank(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "symbol": "600000.SH",
                    "name": " 浦发银行 ",
                    "price": "12.30",
                    "change_pct": "1.25%",
                    "hot_rank": "98",
                },
                {
                    "symbol": "000001.SZ",
                    "name": "平安银行",
                    "price": "11.20",
                    "change_pct": "-0.50%",
                    "hot_rank": "99",
                },
            ]
        )


class FakeStockHotRepository:
    def __init__(self):
        self.rows = pd.DataFrame()

    def upsert_stock_hot_daily(self, rows: pd.DataFrame) -> int:
        self.rows = rows.copy()
        return len(rows)


def test_update_stock_hot_daily_formats_and_saves_rows():
    repository = FakeStockHotRepository()
    service = Service(
        iwencai_provider=FakeIwencaiProvider(),
        stock_hot_repository=repository,
    )

    affected_rows = service.update_stock_hot_daily("20260821")

    assert affected_rows == 2
    assert repository.rows["symbol"].tolist() == ["600000", "000001"]
    assert repository.rows["name"].tolist() == ["浦发银行", "平安银行"]
    assert repository.rows["change_pct"].tolist() == [1.25, -0.5]
    assert repository.rows["hot_value"].tolist() == [98, 99]
    assert repository.rows["trade_date"].tolist() == [
        pd.Timestamp("2026-08-21").date()
    ] * 2
    assert repository.rows["source"].tolist() == ["Iwencai", "Iwencai"]
