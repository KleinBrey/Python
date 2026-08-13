from fastapi import Request

from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


def get_repository(request: Request) -> MarketDataRepository:
    return request.app.state.repository


def get_service(request: Request) -> MarketDataService:
    return request.app.state.market_service

