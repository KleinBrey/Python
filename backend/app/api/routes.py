from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from backend.app.api.dependencies import get_repository, get_service
from backend.app.jobs.tasks import run_sync
from backend.app.repositories import MarketDataRepository
from backend.app.schemas import BarsResponse, MarketStatus, Stock, SyncAccepted
from backend.app.services import MarketDataService

router = APIRouter()

# 使用 Annotated 封装依赖声明，避免每个接口重复书写 Depends。
Repository = Annotated[MarketDataRepository, Depends(get_repository)]
Service = Annotated[MarketDataService, Depends(get_service)]


@router.get("/health")
def health() -> dict[str, str]:
    """返回服务存活状态，供健康检查使用。"""
    return {"status": "ok"}


@router.get("/market/status", response_model=MarketStatus)
def market_status(request: Request, repository: Repository, service: Service) -> dict:
    """汇总本地数据、行情提供方和调度器的运行状态。"""
    scheduler = getattr(request.app.state, "scheduler", None)
    return {
        **repository.status(),
        "provider_configured": service.provider.is_configured(),
        "scheduler_running": bool(scheduler and scheduler.running),
    }


@router.get("/stocks", response_model=list[Stock])
def stocks(
    repository: Repository,
    query: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    """分页查询股票列表，可通过 query 筛选股票。"""
    return repository.list_stocks(query, limit, offset)


@router.get("/market/bars/{symbol}", response_model=BarsResponse)
def bars(
    symbol: str,
    repository: Repository,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(1000, ge=1, le=5000),
) -> dict:
    """查询指定股票的本地日 K 数据。"""
    normalized = normalize_symbol(symbol)
    rows = repository.get_bars(normalized, start_date, end_date, limit)
    if not rows:
        raise HTTPException(status_code=404, detail=f"本地库没有 {normalized} 的日 K")
    return {"symbol": normalized, "adjustment": "none", "rows": rows}


@router.post(
    "/jobs/run", response_model=SyncAccepted, status_code=status.HTTP_202_ACCEPTED
)
def trigger_sync(
    background_tasks: BackgroundTasks,
    service: Service,
    mode: Literal["initial", "daily", "weekly", "monthly"] = "daily",
) -> dict[str, str]:
    """提交一次异步行情同步任务并立即返回受理结果。"""
    # 同步操作可能耗时，因此交给 FastAPI 后台任务执行。
    background_tasks.add_task(run_sync, service, mode)
    return {"status": "accepted", "mode": mode}


def normalize_symbol(value: str) -> str:
    """将六位股票代码转换为带交易所后缀的标准 thscode。"""
    symbol = value.strip().upper()

    # 已包含交易所后缀时直接返回，保留调用方传入的完整代码。
    if "." in symbol:
        return symbol
    if len(symbol) != 6 or not symbol.isdigit():
        raise HTTPException(
            status_code=422, detail="股票代码应为 6 位数字或完整 thscode"
        )

    # 根据证券代码前缀推断北京、上海或深圳证券交易所。
    if symbol.startswith(("4", "8", "92")):
        exchange = "BJ"
    elif symbol.startswith(("5", "6", "9")):
        exchange = "SH"
    else:
        exchange = "SZ"
    return f"{symbol}.{exchange}"
