from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from threading import Lock
from typing import Callable, Literal, TypedDict

import pandas as pd

from backend.app.providers.base import MarketDataProvider
from backend.app.repositories import MarketDataRepository


SyncMode = Literal["initial", "daily", "weekly", "monthly"]


class SyncProgress(TypedDict):
    total: int
    completed: int
    succeeded: int
    failed: int
    rows_written: int
    symbol: str | None


ProgressCallback = Callable[[SyncProgress], None]


class SyncAlreadyRunningError(RuntimeError):
    pass


class MarketDataService:
    def __init__(
        self,
        repository: MarketDataRepository,
        provider: MarketDataProvider,
        *,
        history_days: int = 370,
        workers: int = 4,
    ):
        self.repository = repository
        self.provider = provider
        self.history_days = max(365, history_days)
        self.workers = max(1, min(8, workers))
        self._lock = Lock()

    def sync(
        self,
        mode: SyncMode,
        *,
        symbols: list[str] | None = None,
        limit: int | None = None,
        end_date: date | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> dict:
        if not self._lock.acquire(blocking=False):
            raise SyncAlreadyRunningError("已有行情同步任务正在运行")
        try:
            return self._sync(
                mode,
                symbols=symbols,
                limit=limit,
                end_date=end_date,
                progress_callback=progress_callback,
            )
        finally:
            self._lock.release()

    def _sync(
        self,
        mode: SyncMode,
        *,
        symbols: list[str] | None,
        limit: int | None,
        end_date: date | None,
        progress_callback: ProgressCallback | None,
    ) -> dict:
        if mode not in {"initial", "daily", "weekly", "monthly"}:
            raise ValueError(f"未知同步模式: {mode}")
        if not self.provider.is_configured():
            raise RuntimeError("请在 backend/.env 配置 HITHINK_FINANCE_API_KEY")

        run_id = self.repository.start_sync(mode)
        succeeded = failed = rows_written = 0
        total = 0
        errors: list[str] = []
        try:
            stocks = self.provider.list_stocks()
            self.repository.upsert_stocks(stocks)
            universe = self._resolve_symbols(stocks, symbols)
            if limit is not None:
                universe = universe[: max(0, limit)]
            total = len(universe)
            resolved_end = end_date or date.today()
            starts = self._start_dates(mode, universe, resolved_end)
            self._report_progress(
                progress_callback,
                total=total,
                completed=0,
                succeeded=0,
                failed=0,
                rows_written=0,
                symbol=None,
            )

            with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="hithink-sync") as executor:
                futures = {
                    executor.submit(
                        self.provider.fetch_daily_bars,
                        symbol,
                        starts[symbol].strftime("%Y%m%d"),
                        resolved_end.strftime("%Y%m%d"),
                    ): symbol
                    for symbol in universe
                }
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        frame = self.clean_bars(future.result(), symbol)
                        rows_written += self.repository.upsert_bars(frame)
                        succeeded += 1
                    except Exception as exc:
                        failed += 1
                        if len(errors) < 20:
                            errors.append(f"{symbol}: {exc}")
                    self._report_progress(
                        progress_callback,
                        total=total,
                        completed=succeeded + failed,
                        succeeded=succeeded,
                        failed=failed,
                        rows_written=rows_written,
                        symbol=symbol,
                    )

            status = "success" if failed == 0 else ("partial" if succeeded else "failed")
            message = "; ".join(errors) or None
            self.repository.finish_sync(
                run_id,
                status=status,
                total=total,
                succeeded=succeeded,
                failed=failed,
                rows_written=rows_written,
                message=message,
            )
            return {
                "run_id": run_id,
                "mode": mode,
                "status": status,
                "symbols_total": total,
                "symbols_succeeded": succeeded,
                "symbols_failed": failed,
                "rows_written": rows_written,
                "errors": errors,
            }
        except Exception as exc:
            self.repository.finish_sync(
                run_id,
                status="failed",
                total=total,
                succeeded=succeeded,
                failed=failed,
                rows_written=rows_written,
                message=str(exc),
            )
            raise

    @staticmethod
    def _report_progress(
        callback: ProgressCallback | None,
        *,
        total: int,
        completed: int,
        succeeded: int,
        failed: int,
        rows_written: int,
        symbol: str | None,
    ) -> None:
        if callback is None:
            return
        callback(
            {
                "total": total,
                "completed": completed,
                "succeeded": succeeded,
                "failed": failed,
                "rows_written": rows_written,
                "symbol": symbol,
            }
        )

    def _start_dates(self, mode: SyncMode, symbols: list[str], end_date: date) -> dict[str, date]:
        one_year = end_date - timedelta(days=self.history_days)
        if mode in {"initial", "monthly"}:
            return {symbol: one_year for symbol in symbols}
        if mode == "weekly":
            start = self.repository.recent_trading_date(60) or end_date - timedelta(days=100)
            return {symbol: max(start, one_year) for symbol in symbols}
        latest = self.repository.latest_dates(symbols)
        return {
            symbol: max(one_year, latest.get(symbol, one_year) - timedelta(days=5))
            for symbol in symbols
        }

    @staticmethod
    def _resolve_symbols(stocks: pd.DataFrame, requested: list[str] | None) -> list[str]:
        if not requested:
            return stocks["symbol"].dropna().astype(str).drop_duplicates().tolist()
        by_code = dict(zip(stocks["code"].astype(str), stocks["symbol"].astype(str)))
        result = []
        for raw in requested:
            value = raw.strip().upper()
            symbol = by_code.get(value, value)
            if symbol not in result:
                result.append(symbol)
        return result

    @staticmethod
    def clean_bars(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if frame is None or frame.empty:
            return pd.DataFrame()
        result = frame.copy()
        result = result[result["symbol"] == symbol]
        result["trade_date"] = pd.to_datetime(result["trade_date"], errors="coerce")
        numeric = ["open", "high", "low", "close", "volume"]
        for column in numeric:
            result[column] = pd.to_numeric(result[column], errors="coerce")
        result = result.dropna(subset=["trade_date", *numeric])
        result = result[result["volume"] >= 0]
        result = result[
            (result["high"] >= result[["open", "close", "low"]].max(axis=1))
            & (result["low"] <= result[["open", "close", "high"]].min(axis=1))
        ]
        return (
            result.sort_values("trade_date")
            .drop_duplicates(["symbol", "trade_date", "adjustment"], keep="last")
            .reset_index(drop=True)
        )
