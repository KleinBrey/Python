from fastapi import Request

from backend.app.repository import DailyBarRepository, StockRepository
from backend.app.services import Service


def get_repository(request: Request) -> StockRepository:
    return request.app.state.stock_repository


def get_daily_repository(request: Request) -> DailyBarRepository:
    """取得应用启动时创建的日线 Repository。"""

    return request.app.state.daily_repository


def get_service(request: Request) -> Service:
    return request.app.state.service
