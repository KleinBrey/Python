from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from backend.simple.schemas import Stock
from backend.simple.repository import StockRepository
from backend.simple.services import Service

from .dependencies import get_repository, get_service

router = APIRouter()

# 使用 Annotated 封装依赖声明，避免每个接口重复书写 Depends。
Repository = Annotated[StockRepository, Depends(get_repository)]
Service = Annotated[Service, Depends(get_service)]


@router.get("/stocks", response_model=list[Stock])
def stocks(
    repository: Repository,
    query: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict]:

    print(query, limit, offset)

    # Repository 返回的是 Pandas DataFrame（表格对象）。
    stock_table = repository.get_table_data()

    # FastAPI 不能直接把 DataFrame 当成“股票列表”返回。
    # orient="records" 会把每一行转换成一个字典，最终得到：
    # [{"symbol": "000001.SZ", "name": "平安银行", ...}, ...]
    stock_list = stock_table.to_dict(orient="records")
    return stock_list
