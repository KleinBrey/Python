from __future__ import annotations

import argparse
import json

from tqdm.auto import tqdm

from backend.app.core.config import get_settings
from backend.app.database import DuckDBDatabase
from backend.app.providers import HiThinkMarketDataProvider
from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


def main() -> None:
    parser = argparse.ArgumentParser(description="同步 A 股一年期日 K 到 DuckDB")
    parser.add_argument("--mode", choices=["initial", "daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--symbols", help="逗号分隔的 thscode 或 6 位代码；默认全市场")
    parser.add_argument("--limit", type=int, help="仅处理前 N 只，适合试跑")
    args = parser.parse_args()

    settings = get_settings()
    database = DuckDBDatabase(settings.database_path)
    database.initialize()
    service = MarketDataService(
        MarketDataRepository(database),
        HiThinkMarketDataProvider(
            settings.hithink_finance_api_key,
            settings.hithink_finance_base_url,
            timeout=settings.hithink_timeout_seconds,
            request_interval=settings.hithink_request_interval,
        ),
        history_days=settings.history_days,
        workers=settings.sync_workers,
    )
    symbols = [item.strip() for item in args.symbols.split(",")] if args.symbols else None
    print("正在读取同花顺 A 股证券目录……", flush=True)

    progress_bar: tqdm | None = None
    last_completed = 0

    def display_progress(progress: dict) -> None:
        nonlocal progress_bar, last_completed
        if progress_bar is None:
            progress_bar = tqdm(
                total=progress["total"],
                desc=f"{args.mode} 同步",
                unit="只",
                dynamic_ncols=True,
            )
        increment = progress["completed"] - last_completed
        if increment > 0:
            progress_bar.update(increment)
            last_completed = progress["completed"]
        progress_bar.set_postfix(
            成功=progress["succeeded"],
            失败=progress["failed"],
            写入行=progress["rows_written"],
            当前=progress["symbol"] or "准备中",
            refresh=True,
        )

    try:
        result = service.sync(
            args.mode,
            symbols=symbols,
            limit=args.limit,
            progress_callback=display_progress,
        )
    finally:
        if progress_bar is not None:
            progress_bar.close()

    print("\n同步结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
