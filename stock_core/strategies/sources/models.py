from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class StrategyStock:
    """策略来源统一输出的一只股票。"""

    code: str
    name: str
    market: str
    source_id: str
    source_name: str
    strategy_id: str
    strategy_name: str
    selected_at: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StrategySourceResult:
    """某个策略来源的一次读取结果。"""

    id: str
    name: str
    description: str
    stocks: list[StrategyStock] = field(default_factory=list)
    status: str = "ready"
    updated_at: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_stocks: bool = True) -> dict[str, Any]:
        payload = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "updatedAt": self.updated_at,
            "stockCount": len(self.stocks),
            "error": self.error,
            "metadata": self.metadata,
        }
        if include_stocks:
            payload["stocks"] = [stock.to_dict() for stock in self.stocks]
        return payload


def normalize_stock_code(value: Any) -> tuple[str, str]:
    """把 ``000001.SZ``、``SH600519`` 等格式统一成六位代码和市场。"""

    text = str(value or "").strip().upper()
    match = re.search(r"(?<!\d)(\d{6})(?!\d)", text)
    if not match:
        return "", ""

    code = match.group(1)
    if ".SH" in text or text.startswith("SH"):
        market = "SH"
    elif ".SZ" in text or text.startswith("SZ"):
        market = "SZ"
    elif ".BJ" in text or text.startswith("BJ"):
        market = "BJ"
    elif code.startswith(("6", "9")):
        market = "SH"
    elif code.startswith(("4", "8")):
        market = "BJ"
    else:
        market = "SZ"
    return code, market


def deduplicate_stocks(stocks: list[StrategyStock]) -> list[StrategyStock]:
    seen: set[tuple[str, str, str]] = set()
    result: list[StrategyStock] = []
    for stock in stocks:
        key = (stock.code, stock.source_id, stock.strategy_id)
        if not stock.code or key in seen:
            continue
        seen.add(key)
        result.append(stock)
    return result
