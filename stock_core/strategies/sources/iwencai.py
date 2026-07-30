from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from data.providers.iwencai_api import resolve_output_dir
from stock_core.strategies.sources.models import (
    StrategySourceResult,
    StrategyStock,
    deduplicate_stocks,
    normalize_stock_code,
)


SOURCE_ID = "iwencai"
SOURCE_NAME = "同花顺问财选股"


def resolve_result_file() -> Path:
    explicit_file = os.getenv("IWENCAI_RESULT_FILE", "").strip()
    if explicit_file:
        return Path(explicit_file).expanduser()

    return resolve_output_dir() / "latest.json"


def _stock_from_row(
    row: dict[str, Any],
    *,
    query: str,
    selected_at: str | None,
) -> StrategyStock | None:
    raw_code = row.get("股票代码") or row.get("代码") or row.get("证券代码")
    code, market = normalize_stock_code(raw_code)
    if not code:
        return None

    name = str(row.get("股票简称") or row.get("股票名称") or row.get("名称") or "")
    metrics = {
        key: value
        for key, value in row.items()
        if key not in {"股票代码", "代码", "证券代码", "股票简称", "股票名称", "名称"}
    }
    return StrategyStock(
        code=code,
        name=name,
        market=market,
        source_id=SOURCE_ID,
        source_name=SOURCE_NAME,
        strategy_id="iwencai-query",
        strategy_name=query or "问财选股条件",
        selected_at=selected_at,
        metrics=metrics,
    )


def load_iwencai_source() -> StrategySourceResult:
    result_file = resolve_result_file()
    description = "读取问财选股项目导出的最新 JSON 股票列表"
    if not result_file.is_file():
        return StrategySourceResult(
            id=SOURCE_ID,
            name=SOURCE_NAME,
            description=description,
            status="missing",
            error=f"未找到问财结果文件：{result_file}",
            metadata={"resultFile": str(result_file)},
        )

    try:
        payload = json.loads(result_file.read_text(encoding="utf-8"))
        rows = payload.get("datas") or payload.get("rows") or []
        if not isinstance(rows, list):
            raise ValueError("datas 字段不是股票列表")
        query = str(payload.get("query") or "")
        selected_at = payload.get("fetched_at") or payload.get("updatedAt")
        stocks = [
            stock
            for row in rows
            if isinstance(row, dict)
            if (stock := _stock_from_row(row, query=query, selected_at=selected_at))
        ]
        return StrategySourceResult(
            id=SOURCE_ID,
            name=SOURCE_NAME,
            description=description,
            stocks=deduplicate_stocks(stocks),
            status="online",
            updated_at=selected_at,
            metadata={
                "resultFile": str(result_file),
                "query": query,
                "reportedCount": payload.get("code_count"),
            },
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return StrategySourceResult(
            id=SOURCE_ID,
            name=SOURCE_NAME,
            description=description,
            status="error",
            error=str(exc),
            metadata={"resultFile": str(result_file)},
        )
