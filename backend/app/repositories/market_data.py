from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from backend.app.database import DuckDBDatabase


BAR_COLUMNS = [
    "symbol", "trade_date", "open", "high", "low", "close", "pre_close",
    "change", "pct_change", "volume", "amount", "adjustment", "source", "ingested_at",
]


class MarketDataRepository:
    def __init__(self, database: DuckDBDatabase):
        self.database = database

    def upsert_stocks(self, frame: pd.DataFrame) -> int:
        if frame.empty:
            return 0
        stocks = frame[["symbol", "code", "exchange", "name", "asset_type", "source"]].copy()
        with self.database.write_connection() as connection:
            connection.register("incoming_stocks", stocks)
            connection.execute(
                """
                INSERT INTO stocks (
                    symbol, code, exchange, name, asset_type, source, updated_at
                )
                SELECT symbol, code, exchange, name, asset_type, source, now()
                FROM incoming_stocks
                ON CONFLICT (symbol) DO UPDATE SET
                    code = excluded.code,
                    exchange = excluded.exchange,
                    name = excluded.name,
                    asset_type = excluded.asset_type,
                    source = excluded.source,
                    updated_at = now()
                """
            )
        return len(stocks)

    def upsert_bars(self, frame: pd.DataFrame) -> int:
        if frame.empty:
            return 0
        bars = frame.copy()
        for column in BAR_COLUMNS:
            if column not in bars:
                bars[column] = None
        bars = bars[BAR_COLUMNS]
        bars["trade_date"] = pd.to_datetime(bars["trade_date"]).dt.date
        with self.database.write_connection() as connection:
            connection.register("incoming_bars", bars)
            connection.execute(
                """
                INSERT INTO daily_bars SELECT * FROM incoming_bars
                ON CONFLICT (symbol, trade_date, adjustment) DO UPDATE SET
                    open = excluded.open,
                    high = excluded.high,
                    low = excluded.low,
                    close = excluded.close,
                    pre_close = coalesce(excluded.pre_close, daily_bars.pre_close),
                    change = coalesce(excluded.change, daily_bars.change),
                    pct_change = coalesce(excluded.pct_change, daily_bars.pct_change),
                    volume = excluded.volume,
                    amount = excluded.amount,
                    source = excluded.source,
                    ingested_at = excluded.ingested_at
                """
            )
        return len(bars)

    def list_stocks(self, query: str | None, limit: int, offset: int) -> list[dict[str, Any]]:
        parameters: list[Any] = []
        where = ""
        if query:
            wildcard = f"%{query.strip()}%"
            where = "WHERE symbol ILIKE ? OR code ILIKE ? OR name ILIKE ?"
            parameters.extend([wildcard, wildcard, wildcard])
        parameters.extend([limit, offset])
        with self.database.connection(read_only=True) as connection:
            frame = connection.execute(
                f"""
                SELECT symbol, code, exchange, name, asset_type, source, updated_at
                FROM stocks {where}
                ORDER BY symbol LIMIT ? OFFSET ?
                """,
                parameters,
            ).fetchdf()
        return self._records(frame)

    def get_bars(
        self,
        symbol: str,
        start_date: date | None,
        end_date: date | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        clauses = ["symbol = ?", "adjustment = 'none'"]
        parameters: list[Any] = [symbol]
        if start_date:
            clauses.append("trade_date >= ?")
            parameters.append(start_date)
        if end_date:
            clauses.append("trade_date <= ?")
            parameters.append(end_date)
        parameters.append(limit)
        with self.database.connection(read_only=True) as connection:
            frame = connection.execute(
                f"""
                SELECT trade_date, open, high, low, close, pre_close, change,
                       pct_change, volume, amount
                FROM daily_bars
                WHERE {' AND '.join(clauses)}
                ORDER BY trade_date LIMIT ?
                """,
                parameters,
            ).fetchdf()
        return self._records(frame)

    def latest_dates(self, symbols: list[str]) -> dict[str, date]:
        if not symbols:
            return {}
        requested = pd.DataFrame({"symbol": symbols})
        with self.database.connection() as connection:
            connection.register("requested_symbols", requested)
            rows = connection.execute(
                """
                SELECT b.symbol, max(b.trade_date)
                FROM daily_bars b
                JOIN requested_symbols r USING (symbol)
                WHERE b.adjustment = 'none'
                GROUP BY b.symbol
                """
            ).fetchall()
        return dict(rows)

    def recent_trading_date(self, sessions: int) -> date | None:
        with self.database.connection(read_only=True) as connection:
            row = connection.execute(
                """
                SELECT min(trade_date) FROM (
                    SELECT DISTINCT trade_date FROM daily_bars
                    ORDER BY trade_date DESC LIMIT ?
                )
                """,
                [sessions],
            ).fetchone()
        return row[0] if row else None

    def status(self) -> dict[str, Any]:
        with self.database.connection(read_only=True) as connection:
            stock_count = connection.execute("SELECT count(*) FROM stocks").fetchone()[0]
            bar_stats = connection.execute(
                "SELECT count(*), count(DISTINCT symbol), min(trade_date), max(trade_date) FROM daily_bars"
            ).fetchone()
            latest_sync = connection.execute(
                """
                SELECT id, mode, status, started_at, finished_at, symbols_total,
                       symbols_succeeded, symbols_failed, rows_written, message
                FROM sync_runs ORDER BY id DESC LIMIT 1
                """
            ).fetchdf()
        return {
            "database_path": str(self.database.path),
            "stock_count": stock_count,
            "bar_count": bar_stats[0],
            "bar_symbol_count": bar_stats[1],
            "first_trade_date": bar_stats[2],
            "last_trade_date": bar_stats[3],
            "latest_sync": self._records(latest_sync)[0] if not latest_sync.empty else None,
        }

    def start_sync(self, mode: str) -> int:
        with self.database.write_connection() as connection:
            return connection.execute(
                "INSERT INTO sync_runs(mode, status) VALUES (?, 'running') RETURNING id",
                [mode],
            ).fetchone()[0]

    def finish_sync(
        self,
        run_id: int,
        *,
        status: str,
        total: int,
        succeeded: int,
        failed: int,
        rows_written: int,
        message: str | None,
    ) -> None:
        with self.database.write_connection() as connection:
            connection.execute(
                """
                UPDATE sync_runs
                SET status = ?, finished_at = CURRENT_TIMESTAMP, symbols_total = ?,
                    symbols_succeeded = ?, symbols_failed = ?, rows_written = ?, message = ?
                WHERE id = ?
                """,
                [status, total, succeeded, failed, rows_written, message, run_id],
            )

    @staticmethod
    def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
        if frame.empty:
            return []
        clean = frame.astype(object).where(pd.notnull(frame), None)
        records = clean.to_dict(orient="records")
        for record in records:
            for key, value in record.items():
                if isinstance(value, (pd.Timestamp, datetime, date)):
                    record[key] = value.isoformat()
                elif hasattr(value, "item"):
                    record[key] = value.item()
        return records
