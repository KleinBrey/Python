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

    # Service 会依次完成以下工作：
    # 1. 从 Tushare 获取最新股票列表；
    # 2. 将数据整理成数据库需要的格式；
    # 3. 新增股票，或者更新数据库中已经存在的股票。
    service.update_stocks_list()

    # 只有上面的更新操作没有抛出异常时，才会执行到这里。
    return {
        "status": "success",
        "message": "股票列表更新成功",
    }
