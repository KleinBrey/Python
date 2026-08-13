from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class MarketDataProvider(ABC):
    source_id: str

    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    def list_stocks(self) -> pd.DataFrame: ...

    @abstractmethod
    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame: ...

