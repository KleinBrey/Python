from fastapi import Request

from backend.simple.repository import StockRepository
from backend.simple.services import Service


def get_repository(request: Request) -> StockRepository:
    return request.app.state.stock_repository


def get_service(request: Request) -> Service:
    return request.app.state.service
