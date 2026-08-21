from __future__ import annotations

from threading import Event

from backend.app.core.config import get_settings
from backend.app.database import DuckDBDatabase
from backend.app.jobs import create_scheduler
from backend.app.providers import HiThinkMarketDataProvider
from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


def main() -> None:
    settings = get_settings()
    database = DuckDBDatabase(settings.database_path)
    database.initialize()
    service = MarketDataService(
        MarketDataRepository(database),
        HiThinkMarketDataProvider(
            settings.hithink_finance_api_key,
            settings.hithink_finance_base_url,
            timeout=settings.hithink_timeout_seconds,
        ),
        history_days=settings.history_days,
        workers=settings.sync_workers,
    )
    scheduler = create_scheduler(settings, service)
    scheduler.start()
    print("调度器已启动；Ctrl+C 停止")
    try:
        Event().wait()
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()

