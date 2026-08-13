from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import router
from backend.app.core.config import get_settings
from backend.app.database import DuckDBDatabase
from backend.app.jobs import create_scheduler
from backend.app.providers import HiThinkMarketDataProvider
from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    database = DuckDBDatabase(settings.database_path)
    database.initialize()
    repository = MarketDataRepository(database)
    provider = HiThinkMarketDataProvider(
        settings.hithink_finance_api_key,
        settings.hithink_finance_base_url,
        timeout=settings.hithink_timeout_seconds,
        request_interval=settings.hithink_request_interval,
    )
    service = MarketDataService(
        repository,
        provider,
        history_days=settings.history_days,
        workers=settings.sync_workers,
    )
    scheduler = create_scheduler(settings, service)
    app.state.repository = repository
    app.state.market_service = service
    app.state.scheduler = scheduler
    if settings.scheduler_enabled:
        scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs"}

