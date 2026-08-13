from datetime import date, datetime

from pydantic import BaseModel


class Stock(BaseModel):
    symbol: str
    code: str
    exchange: str
    name: str | None = None
    asset_type: str
    source: str
    updated_at: datetime


class Bar(BaseModel):
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    pre_close: float | None = None
    change: float | None = None
    pct_change: float | None = None
    volume: float
    amount: float | None = None


class BarsResponse(BaseModel):
    symbol: str
    adjustment: str = "none"
    rows: list[Bar]


class MarketStatus(BaseModel):
    database_path: str
    provider_configured: bool
    scheduler_running: bool
    stock_count: int
    bar_count: int
    bar_symbol_count: int
    first_trade_date: date | None = None
    last_trade_date: date | None = None
    latest_sync: dict | None = None


class SyncAccepted(BaseModel):
    status: str
    mode: str

