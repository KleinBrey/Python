from datetime import date, datetime

from pydantic import BaseModel


class Stock(BaseModel):
    symbol: str
    name: str
    exchange: str
    market: str
    type: str
    source: str
    update_time: datetime


class DailyBar(BaseModel):
    """一只股票单个交易日的日 K 线。"""

    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float | None = None
    source: str
