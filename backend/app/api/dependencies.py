from fastapi import Request

from backend.app.repository import (
    DailyBarRepository,
    StockHotDailyRepository,
    StockRepository,
)
from backend.app.services import Service


def get_stock_repository(request: Request) -> StockRepository:
    return request.app.state.stock_repository


def get_daily_repository(request: Request) -> DailyBarRepository:
    return request.app.state.daily_repository


def get_stock_hot_repository(request: Request) -> StockHotDailyRepository:
    return request.app.state.stock_hot_repository


def get_service(request: Request) -> Service:
    return request.app.state.service
