from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


# 市场数据提供者的抽象基类，用于统一不同数据源的调用方式。
class MarketDataProvider(ABC):
    # 数据源的唯一标识，会随股票和行情数据写入数据库。
    source_id: str

    # 检查数据源是否已具备 API 密钥等必要配置。
    @abstractmethod
    def is_configured(self) -> bool: ...

    # 获取股票目录，返回包含代码、交易所、名称和数据源等字段的数据表。
    @abstractmethod
    def list_stocks(self) -> pd.DataFrame: ...

    # 获取指定证券在 YYYYMMDD 日期范围内的日线行情数据。
    @abstractmethod
    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame: ...
