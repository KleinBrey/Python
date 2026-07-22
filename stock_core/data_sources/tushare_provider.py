from __future__ import annotations

import os
from functools import lru_cache

import pandas as pd
import tushare as ts


@lru_cache(maxsize=1)
def get_client():
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("请先设置环境变量 TUSHARE_TOKEN，再运行 Tushare 数据流水线。")
    return ts.pro_api(token)


def fetch_basic_stock_pool(fields: list[str]) -> pd.DataFrame:
    return get_client().bak_basic(
        trade_date="",
        ts_code="",
        limit="",
        offset="",
        fields=fields,
    )


def fetch_daily_stock_data(
    ts_code: str,
    start_date: str,
    end_date: str,
    fields: list[str],
) -> pd.DataFrame:
    return get_client().daily(
        ts_code=ts_code,
        start_date=start_date,
        end_date=end_date,
        fields=fields,
    )
