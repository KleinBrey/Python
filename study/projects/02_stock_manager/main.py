"""
==================================================
综合实战 2：A 股行情管理（Provider + Service + SQLite + logging）
==================================================
"""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Protocol

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

class MarketDataError(RuntimeError):
    pass

@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float

class Provider(Protocol):
    def fetch(self, symbol: str) -> Quote: ...

class DemoProvider:
    def fetch(self, symbol: str) -> Quote:
        prices = {"600519": 1688.0, "000001": 10.5}
        if symbol not in prices:
            raise MarketDataError(f"没有 {symbol} 的演示行情")
        return Quote(symbol, prices[symbol])

class QuoteRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS quotes(symbol TEXT PRIMARY KEY, price REAL NOT NULL)"
        )

    def save(self, quote: Quote) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO quotes VALUES (?, ?)", (quote.symbol, quote.price)
        )
        self.connection.commit()

    def all(self) -> list[Quote]:
        rows = self.connection.execute("SELECT symbol, price FROM quotes ORDER BY symbol")
        return [Quote(symbol, price) for symbol, price in rows]

class QuoteService:
    def __init__(self, provider: Provider, repository: QuoteRepository):
        self.provider = provider
        self.repository = repository

    def refresh(self, symbols: list[str]) -> None:
        for symbol in symbols:
            try:
                quote = self.provider.fetch(symbol)
                self.repository.save(quote)
                logger.info("已保存 %s %.2f", quote.symbol, quote.price)
            except MarketDataError as error:
                logger.warning("跳过：%s", error)

def main() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        repository = QuoteRepository(connection)
        QuoteService(DemoProvider(), repository).refresh(["600519", "000001", "999999"])
        for quote in repository.all():
            print(quote)
    finally:
        connection.close()

if __name__ == "__main__":
    main()
