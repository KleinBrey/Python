from datetime import datetime

from pydantic import BaseModel


class Stock(BaseModel):
    symbol: str
    name: str
    exchange: str
    market: str
    type: str
    source: str
    update_time: datetime
