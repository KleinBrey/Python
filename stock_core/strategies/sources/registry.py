from __future__ import annotations

from collections.abc import Callable

from stock_core.strategies.sources.handwritten import load_handwritten_source
from stock_core.strategies.sources.iwencai import load_iwencai_source
from stock_core.strategies.sources.models import StrategySourceResult


SOURCE_LOADERS: dict[str, Callable[[], StrategySourceResult]] = {
    "iwencai": load_iwencai_source,
    "handwritten": load_handwritten_source,
}


def load_strategy_sources(source_ids: list[str] | None = None) -> list[StrategySourceResult]:
    selected_ids = source_ids or list(SOURCE_LOADERS)
    unknown = [source_id for source_id in selected_ids if source_id not in SOURCE_LOADERS]
    if unknown:
        raise ValueError(f"未知策略来源：{', '.join(unknown)}")
    return [SOURCE_LOADERS[source_id]() for source_id in selected_ids]
