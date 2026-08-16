"""市场行情同步服务。

这个文件负责协调三个步骤：
1. 从数据提供者获取股票和日 K 线数据。
2. 清洗不完整或不合理的日 K 线数据。
3. 把清洗后的数据交给仓储层保存到数据库。
"""

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
    """一次进度通知中包含的数据。"""

    total: int
    completed: int
    succeeded: int
    failed: int
    rows_written: int
    symbol: str | None


ProgressCallback = Callable[[SyncProgress], None]


class SyncAlreadyRunningError(RuntimeError):
    """已经有同步任务运行时抛出的异常。"""


class MarketDataService:
    """负责获取、清洗并保存市场行情数据。"""

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

        # 至少同步 365 天的历史数据。
        if history_days < 365:
            self.history_days = 365
        else:
            self.history_days = history_days

        # 并发线程数最少为 1，最多为 8，避免请求过多。
        if workers < 1:
            self.workers = 1
        elif workers > 8:
            self.workers = 8
        else:
            self.workers = workers

        # 同一时间只允许执行一个同步任务。
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
        """执行一次行情同步，并返回同步结果。"""

        # blocking=False 表示不等待锁：如果已有任务，立即报错。
        lock_acquired = self._lock.acquire(blocking=False)
        if not lock_acquired:
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
            # 无论同步成功还是失败，都必须释放锁。
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
        """完成同步工作的内部方法。"""

        # 先检查调用参数和数据源配置。
        if mode not in {"initial", "daily", "weekly", "monthly"}:
            raise ValueError(f"未知同步模式: {mode}")

        if not self.provider.is_configured():
            raise RuntimeError("请在 backend/.env 配置 HITHINK_FINANCE_API_KEY")

        # 先在数据库中创建一条“正在运行”的同步记录。
        run_id = self.repository.start_sync(mode)

        succeeded = 0
        failed = 0
        rows_written = 0
        total = 0
        errors: list[str] = []

        try:
            # 获取最新股票目录，并新增或更新到数据库。
            stocks = self.provider.list_stocks()
            self.repository.upsert_stocks(stocks)

            # 决定本次需要同步哪些股票。
            universe = self._resolve_symbols(stocks, symbols)
            if limit is not None:
                safe_limit = max(0, limit)
                universe = universe[:safe_limit]

            total = len(universe)

            # 没有传结束日期时，默认同步到今天。
            resolved_end = end_date or date.today()
            starts = self._start_dates(mode, universe, resolved_end)

            # 先发送一次初始进度，让调用者知道任务总数。
            self._report_progress(
                progress_callback,
                total=total,
                completed=0,
                succeeded=0,
                failed=0,
                rows_written=0,
                symbol=None,
            )

            # 使用线程池并发请求多只股票，提高同步速度。
            with ThreadPoolExecutor(
                max_workers=self.workers,
                thread_name_prefix="hithink-sync",
            ) as executor:
                # 保存“任务 -> 股票代码”的对应关系。
                futures = {}

                for symbol in universe:
                    start_text = starts[symbol].strftime("%Y%m%d")
                    end_text = resolved_end.strftime("%Y%m%d")

                    future = executor.submit(
                        self.provider.fetch_daily_bars,
                        symbol,
                        start_text,
                        end_text,
                    )
                    futures[future] = symbol

                # as_completed 会按照请求完成的先后顺序返回任务。
                for future in as_completed(futures):
                    symbol = futures[future]

                    try:
                        original_frame = future.result()
                        clean_frame = self.clean_bars(original_frame, symbol)
                        written = self.repository.upsert_bars(clean_frame)

                        rows_written += written
                        succeeded += 1
                    except Exception as exc:
                        failed += 1

                        # 最多保存 20 条错误，避免返回内容过长。
                        if len(errors) < 20:
                            errors.append(f"{symbol}: {exc}")

                    # 每完成一只股票，就通知一次当前进度。
                    self._report_progress(
                        progress_callback,
                        total=total,
                        completed=succeeded + failed,
                        succeeded=succeeded,
                        failed=failed,
                        rows_written=rows_written,
                        symbol=symbol,
                    )

            # 根据成功和失败数量判断本次任务状态。
            if failed == 0:
                status = "success"
            elif succeeded > 0:
                status = "partial"
            else:
                status = "failed"

            message = "; ".join(errors) or None

            # 更新数据库中的同步记录。
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
            # 整个任务出现意外错误时，也要把失败状态写入数据库。
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
        """如果调用者提供了回调函数，就向它发送最新进度。"""

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
        """根据同步模式，计算每只股票的开始日期。"""

        earliest_date = end_date - timedelta(days=self.history_days)

        # 初始化和月度同步重新获取完整的历史区间。
        if mode in {"initial", "monthly"}:
            start_dates = {}
            for symbol in symbols:
                start_dates[symbol] = earliest_date
            return start_dates

        # 周度同步重新检查最近约 60 个交易日的数据。
        if mode == "weekly":
            recent_date = self.repository.recent_trading_date(60)
            if recent_date is None:
                recent_date = end_date - timedelta(days=100)

            start = max(recent_date, earliest_date)
            start_dates = {}
            for symbol in symbols:
                start_dates[symbol] = start
            return start_dates

        # 日度同步从数据库中每只股票的最新日期往前检查 5 天。
        latest = self.repository.latest_dates(symbols)
        start_dates = {}

        for symbol in symbols:
            latest_date = latest.get(symbol, earliest_date)
            recheck_date = latest_date - timedelta(days=5)
            start_dates[symbol] = max(earliest_date, recheck_date)

        return start_dates

    @staticmethod
    def _resolve_symbols(stocks: pd.DataFrame, requested: list[str] | None) -> list[str]:
        """把用户输入的 6 位代码转换为数据源使用的完整代码。"""

        # 没有指定股票时，同步股票目录中的全部股票。
        if not requested:
            symbols = stocks["symbol"]
            symbols = symbols.dropna()
            symbols = symbols.astype(str)
            symbols = symbols.drop_duplicates()
            return symbols.tolist()

        # 例如把 000001 转换为 000001.SZ。
        by_code = dict(zip(stocks["code"].astype(str), stocks["symbol"].astype(str)))

        result: list[str] = []
        for raw in requested:
            value = raw.strip().upper()
            symbol = by_code.get(value, value)

            # 保留输入顺序，同时去掉重复股票。
            if symbol not in result:
                result.append(symbol)

        return result

    @staticmethod
    def clean_bars(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """清洗一只股票的日 K 线数据。"""

        # 数据源没有返回数据时，直接返回空表。
        if frame is None or frame.empty:
            return pd.DataFrame()

        # 使用副本，避免修改数据源返回的原始 DataFrame。
        result = frame.copy()

        # 只保留当前股票的数据。
        result = result[result["symbol"] == symbol]

        # 无法转换的日期和数字会变成 NaT 或 NaN，稍后统一删除。
        result["trade_date"] = pd.to_datetime(result["trade_date"], errors="coerce")
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for column in numeric_columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")

        # 删除日期或必要数字缺失的记录，并排除负成交量。
        required_columns = ["trade_date", *numeric_columns]
        result = result.dropna(subset=required_columns)
        result = result[result["volume"] >= 0]

        # 最高价不能低于开盘价、收盘价和最低价。
        other_high_prices = result[["open", "close", "low"]].max(axis=1)
        high_is_valid = result["high"] >= other_high_prices

        # 最低价不能高于开盘价、收盘价和最高价。
        other_low_prices = result[["open", "close", "high"]].min(axis=1)
        low_is_valid = result["low"] <= other_low_prices

        result = result[high_is_valid & low_is_valid]

        # 按日期排序；同一天有重复数据时保留最后一条。
        result = result.sort_values("trade_date")
        result = result.drop_duplicates(
            ["symbol", "trade_date", "adjustment"],
            keep="last",
        )
        result = result.reset_index(drop=True)

        return result
