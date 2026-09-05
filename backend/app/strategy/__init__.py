"""股票策略模块。"""

from .registry import (
    STRATEGY_EXECUTORS,
    execute_strategy,
    find_strategy,
    strategy_list,
)

__all__ = [
    "STRATEGY_EXECUTORS",
    "execute_strategy",
    "find_strategy",
    "strategy_list",
]
