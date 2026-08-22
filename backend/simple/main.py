from __future__ import annotations
from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.simple.api import router
from backend.simple.config.config import get_settings
from backend.simple.database import DuckDBDatabase
from backend.simple.provider import HithinkProvider, TushareProvider
from backend.simple.repository import DailyBarRepository, StockRepository
from backend.simple.services import Service

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # 初始化数据库
    database = DuckDBDatabase()
    database.initialize()

    # 注册stock表的repository，用来统一处理增删改查
    stock_repository = StockRepository(database)
    daily_repository = DailyBarRepository(database)

    # 注册API调用
    hithink_provider = HithinkProvider()

    tushare_provider = TushareProvider()

    # 业务逻辑处理
    service = Service(
        hithink_provider, tushare_provider, stock_repository, daily_repository
    )

    # 将共享实例挂载到 app.state，供路由及其他应用组件复用。
    app.state.stock_repository = stock_repository
    app.state.service = service

    # yield 之前的代码会在应用启动时执行。
    # 执行到 yield 后，FastAPI 开始正常接收和处理请求。
    # 当应用关闭时，程序会从 yield 后面继续执行清理代码。
    # 当前没有需要手动关闭的资源，所以 yield 后暂时不需要其他代码。
    yield


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
