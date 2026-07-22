from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from stock_core.strategies.sources.models import (
    StrategySourceResult,
    StrategyStock,
    deduplicate_stocks,
    normalize_stock_code,
)


SOURCE_ID = "handwritten"
SOURCE_NAME = "手写策略"
StrategyLoader = Callable[[], Iterable[dict[str, Any]]]


@dataclass(frozen=True, slots=True)
class HandwrittenStrategy:
    id: str
    name: str
    loader: StrategyLoader


_STRATEGIES: list[HandwrittenStrategy] = []


def register_handwritten_strategy(strategy_id: str, name: str):
    """注册一个返回字典列表的手写策略。"""

    def decorator(loader: StrategyLoader) -> StrategyLoader:
        _STRATEGIES.append(HandwrittenStrategy(strategy_id, name, loader))
        return loader

    return decorator


@register_handwritten_strategy("volume-spike", "量能放大策略")
def load_volume_spike_results() -> Iterable[dict[str, Any]]:
    """读取现有量能放大策略保存到 MongoDB 的结果。"""

    from stock_core.database import collections as database

    return database.stock_filter_result.find_many({})


def _stock_from_record(
    record: dict[str, Any],
    strategy: HandwrittenStrategy,
) -> StrategyStock | None:
    raw_code = (
        record.get("股票代码")
        or record.get("代码")
        or record.get("证券代码")
        or record.get("code")
    )
    code, market = normalize_stock_code(raw_code)
    if not code:
        return None

    name = str(
        record.get("股票名称")
        or record.get("股票简称")
        or record.get("名称")
        or record.get("name")
        or ""
    )
    selected_at = record.get("交易日期") or record.get("selectedAt") or record.get("updatedAt")
    excluded = {"_id", "股票代码", "代码", "证券代码", "code", "股票名称", "股票简称", "名称", "name"}
    return StrategyStock(
        code=code,
        name=name,
        market=market,
        source_id=SOURCE_ID,
        source_name=SOURCE_NAME,
        strategy_id=strategy.id,
        strategy_name=strategy.name,
        selected_at=str(selected_at) if selected_at is not None else None,
        metrics={key: value for key, value in record.items() if key not in excluded},
    )


def load_handwritten_source() -> StrategySourceResult:
    stocks: list[StrategyStock] = []
    errors: list[str] = []
    for strategy in _STRATEGIES:
        try:
            records = strategy.loader()
            for record in records:
                if not isinstance(record, dict):
                    continue
                stock = _stock_from_record(record, strategy)
                if stock:
                    stocks.append(stock)
        except Exception as exc:
            message = str(exc)
            if "27017" in message or "MongoDB" in message:
                message = "MongoDB 未连接，暂无已保存的策略结果"
            errors.append(f"{strategy.name}: {message}")

    return StrategySourceResult(
        id=SOURCE_ID,
        name=SOURCE_NAME,
        description="运行或读取项目内 Python 手写策略的股票列表",
        stocks=deduplicate_stocks(stocks),
        status="online" if not errors else ("degraded" if stocks else "offline"),
        error="；".join(errors) or None,
        metadata={
            "strategies": [
                {"id": strategy.id, "name": strategy.name}
                for strategy in _STRATEGIES
            ]
        },
    )
