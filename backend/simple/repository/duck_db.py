"""DuckDB 数据仓库层。

Repository 只负责数据库读写，不负责调用第三方接口或清洗业务数据。
每张表的冲突键和更新字段不同，因此由具体 Repository 明确实现写入逻辑。
"""

import pandas as pd

from backend.simple.database import DuckDBDatabase

STOCK_COLUMNS = ["symbol", "name", "exchange", "market", "type", "source"]

DAILY_BAR_COLUMNS = [
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


def _require_columns(rows: pd.DataFrame, required_columns: list[str]) -> None:
    """检查入库数据是否包含指定字段。"""

    missing_columns = [
        column for column in required_columns if column not in rows.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"入库数据缺少字段：{missing_text}")


class BaseRepository:
    """保存具体 Repository 共用的数据库依赖。"""

    def __init__(self, db: DuckDBDatabase):
        self.db = db


class StockRepository(BaseRepository):
    """负责 stocks 表的读写。"""

    def get_table_data(self) -> pd.DataFrame:
        """获取全部股票基础信息。"""

        with self.db.connection(read_only=True) as connection:
            return connection.execute("SELECT * FROM stocks ORDER BY symbol").df()

    def upsert_stocks(self, rows: pd.DataFrame) -> int:
        """新增或更新股票基础信息，返回处理的行数。"""

        if rows.empty:
            return 0

        _require_columns(rows, STOCK_COLUMNS)
        stocks = rows[STOCK_COLUMNS].copy()

        with self.db.connection() as connection:
            connection.register("incoming_stocks", stocks)
            connection.execute("""
                INSERT INTO stocks (
                    symbol,
                    name,
                    exchange,
                    market,
                    type,
                    source
                )
                SELECT
                    symbol,
                    name,
                    exchange,
                    market,
                    type,
                    source
                FROM incoming_stocks
                ON CONFLICT (symbol) DO UPDATE SET
                    name = excluded.name,
                    exchange = excluded.exchange,
                    market = excluded.market,
                    type = excluded.type,
                    source = excluded.source,
                    update_time = now()
                """)

        return len(stocks)

    def insert_stocks(self, rows: pd.DataFrame) -> int:
        """兼容原有调用；实际执行新增或更新。"""

        return self.upsert_stocks(rows)


class DailyBarRepository(BaseRepository):
    """负责 daily_bars 表的读写。"""

    def get_table_data(self) -> pd.DataFrame:
        """获取全部日线数据。"""

        with self.db.connection(read_only=True) as connection:
            return connection.execute(
                "SELECT * FROM daily_bars ORDER BY symbol, date"
            ).df()

    def upsert_daily_bars(self, rows: pd.DataFrame) -> int:
        """新增或更新日线数据，返回处理的行数。"""

        if rows.empty:
            return 0

        # amount 是表中的可选字段，数据源未提供时使用空值。
        bars = rows.copy()
        if "amount" not in bars.columns:
            bars["amount"] = None

        _require_columns(bars, DAILY_BAR_COLUMNS)
        bars = bars[DAILY_BAR_COLUMNS]

        # DuckDB 的目标字段是 DATE；无效日期会在这里明确报错。
        bars["date"] = pd.to_datetime(bars["date"], errors="raise").dt.date

        with self.db.connection() as connection:
            connection.register("incoming_daily_bars", bars)
            connection.execute("""
                INSERT INTO daily_bars (
                    symbol,
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    amount,
                    source
                )
                SELECT
                    symbol,
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    amount,
                    source
                FROM incoming_daily_bars
                ON CONFLICT (symbol, date) DO UPDATE SET
                    open = excluded.open,
                    high = excluded.high,
                    low = excluded.low,
                    close = excluded.close,
                    volume = excluded.volume,
                    amount = excluded.amount,
                    source = excluded.source,
                    update_time = now()
                """)

        return len(bars)

    def insert_daily_bars(self, rows: pd.DataFrame) -> int:
        """兼容 insert 风格命名；实际执行新增或更新。"""

        return self.upsert_daily_bars(rows)
