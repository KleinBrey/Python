"""策略配置和执行入口。"""

import json
from pathlib import Path

from .implementations.panic_reversal import run_strategy as run_panic_reversal
from .implementations.volume_1_5x import run_strategy as run_volume_1_5x

CONFIG_PATH = Path(__file__).with_name("strategies.json")

STRATEGY_EXECUTORS = {
    "panic-reversal": run_panic_reversal,
    "volume-1-5x": run_volume_1_5x,
}


def strategy_list() -> list[dict[str, object]]:
    """策略列表"""
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)["strategies"]


def find_strategy(strategy_id: str) -> dict[str, object]:
    """查询策略"""
    for strategy in strategy_list():
        if strategy["id"] == strategy_id:
            return strategy
    raise KeyError(strategy_id)


def execute_strategy(strategy_id: str, **inputs):
    """执行策略"""
    return STRATEGY_EXECUTORS[strategy_id](**inputs)
