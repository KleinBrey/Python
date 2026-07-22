"""统一的策略股票来源。

所有来源都输出 ``StrategyStock``，上层无需关心股票来自问财文件还是手写策略。
"""

from stock_core.strategies.sources.registry import load_strategy_sources

__all__ = ["load_strategy_sources"]
