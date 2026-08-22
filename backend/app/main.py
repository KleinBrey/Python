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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """初始化应用依赖，并在应用关闭时释放后台任务。"""
    settings = get_settings()

    # 按照数据库 -> 仓储 -> 数据提供方 -> 服务的顺序装配业务依赖。
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

    # 将共享实例挂载到 app.state，供路由及其他应用组件复用。
    app.state.repository = repository
    app.state.market_service = service
    app.state.scheduler = scheduler

    # 可通过配置关闭定时任务，便于本地开发和测试。
    if settings.scheduler_enabled:
        scheduler.start()
    try:
        yield
    finally:
        # 非阻塞关闭调度器，避免应用退出时仍有后台线程运行。
        if scheduler.running:
            scheduler.shutdown(wait=False)


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

# 允许配置中声明的前端来源跨域访问 API。
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
    """返回服务基本信息和交互式 API 文档入口。"""
    return {"name": settings.app_name, "docs": "/docs"}
