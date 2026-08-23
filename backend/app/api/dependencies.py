from fastapi import Request

from backend.app.repository import StockRepository
from backend.app.services import Service


def get_repository(request: Request) -> StockRepository:
    return request.app.state.stock_repository


def get_service(request: Request) -> Service:
    return request.app.state.service
