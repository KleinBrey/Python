from __future__ import annotations

import argparse

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
    print(service.sync(args.mode, symbols=symbols, limit=args.limit))


if __name__ == "__main__":
    main()

