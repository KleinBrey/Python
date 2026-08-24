from __future__ import annotations

from datetime import date
from typing import Annotated

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from backend.app.schemas import DailyBar, Stock
from backend.app.repository import DailyBarRepository, StockRepository
from backend.app.services import Service
from backend.app.utils.symbol import validate_symbol

from .dependencies import get_daily_repository, get_repository, get_service

router = APIRouter()

# 使用 Annotated 封装依赖声明，避免每个接口重复书写 Depends。
Repository = Annotated[StockRepository, Depends(get_repository)]
DailyRepository = Annotated[DailyBarRepository, Depends(get_daily_repository)]
dbService = Annotated[Service, Depends(get_service)]


@router.get("/stocks-list", response_model=list[Stock])
def stocks(
    repository: Repository,
    query: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict]:

    print(query, limit, offset)

    # Repository 返回的是 Pandas DataFrame（表格对象）。
    stock_table = repository.get_table_data().head(100)

    # FastAPI 不能直接把 DataFrame 当成“股票列表”返回。
    # orient="records" 会把每一行转换成一个字典，最终得到：
    # [{"symbol": "000001.SZ", "name": "平安银行", ...}, ...]
    stock_list = stock_table.to_dict(orient="records")
    return stock_list


@router.post("/stocks-list")
def update_stocks_list(service: dbService) -> dict[str, str]:
    """从数据源获取最新股票列表，并保存到本地数据库。"""

    service.update_stocks_list()

    # 只有上面的更新操作没有抛出异常时，才会执行到这里。
    return {
        "status": "success",
        "message": "股票列表更新成功",
    }


@router.get("/daily-bars", response_model=list[DailyBar])
def daily_bars(
    repository: DailyRepository,
    symbol: Annotated[
        str,
        Query(description="股票代码，例如 600519 或 600519.SH"),
    ],
    start_date: Annotated[
        date,
        Query(description="开始日期，格式 YYYY-MM-DD，包含当天"),
    ],
    end_date: Annotated[
        date,
        Query(description="结束日期，格式 YYYY-MM-DD，包含当天"),
    ],
) -> list[dict]:
    """从本地数据库查询指定股票、指定日期范围内的日 K 线。"""

    if start_date > end_date:
        raise HTTPException(status_code=422, detail="开始日期不能晚于结束日期")

    try:
        normalized_symbol = validate_symbol(symbol)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    daily_bar_table = repository.get_by_symbol_and_date_range(
        normalized_symbol,
        start_date,
        end_date,
    )

    # DuckDB 的空成交额在 DataFrame 中通常表现为 NaN。JSON 没有 NaN，
    # 因此返回前明确转换为 null，交给 DailyBar 响应模型继续校验字段类型。
    records = daily_bar_table.to_dict(orient="records")
    for record in records:
        if pd.isna(record["amount"]):
            record["amount"] = None

    return records
