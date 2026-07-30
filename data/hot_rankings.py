"""同花顺扶摇官方热榜注册表。"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from data.providers import hithink_financial


_HOT_LIST_DOC = "https://fuyao.aicubes.cn/docs/api-reference/hot-list-data/"
_LIMIT_UP_DOC = "https://fuyao.aicubes.cn/docs/api-reference/limit-up-data/"

HOT_RANKINGS: list[dict[str, Any]] = [
    {
        "id": "ths-hot-day",
        "title": "同花顺 24 小时热股榜",
        "source": "同花顺扶摇",
        "provider": hithink_financial.SOURCE_ID,
        "description": "A 股热股榜 Top30，24 小时级别",
        "function": "hot-stock-list",
        "endpoint": "/api/a-share/special-data/hot-stock-list",
        "params": {"period": "day"},
        "docUrl": _HOT_LIST_DOC,
    },
    {
        "id": "ths-hot-hour",
        "title": "同花顺小时热股榜",
        "source": "同花顺扶摇",
        "provider": hithink_financial.SOURCE_ID,
        "description": "A 股热股榜 Top30，小时级别",
        "function": "hot-stock-list",
        "endpoint": "/api/a-share/special-data/hot-stock-list",
        "params": {"period": "hour"},
        "docUrl": _HOT_LIST_DOC,
    },
    {
        "id": "ths-skyrocket-day",
        "title": "同花顺日飙升榜",
        "source": "同花顺扶摇",
        "provider": hithink_financial.SOURCE_ID,
        "description": "A 股热度排名日飙升榜 Top30",
        "function": "skyrocket-list",
        "endpoint": "/api/a-share/special-data/skyrocket-list",
        "params": {"period": "day"},
        "docUrl": _HOT_LIST_DOC,
    },
    {
        "id": "ths-skyrocket-hour",
        "title": "同花顺小时飙升榜",
        "source": "同花顺扶摇",
        "provider": hithink_financial.SOURCE_ID,
        "description": "A 股热度排名小时飙升榜 Top30",
        "function": "skyrocket-list",
        "endpoint": "/api/a-share/special-data/skyrocket-list",
        "params": {"period": "hour"},
        "docUrl": _HOT_LIST_DOC,
    },
    {
        "id": "ths-limit-up",
        "title": "同花顺涨停股票池",
        "source": "同花顺扶摇",
        "provider": hithink_financial.SOURCE_ID,
        "description": "官方涨停与连板股票池，按涨停时间倒序",
        "function": "limit-up-pool",
        "endpoint": "/api/a-share/special-data/limit-up-pool",
        "params": {
            "page": 1,
            "size": 200,
            "sort_field": "limit_up_time",
            "sort_dir": "desc",
        },
        "docUrl": _LIMIT_UP_DOC,
    },
]


def resolve_params(params: dict[str, Any] | Callable[[], dict[str, Any]]) -> dict[str, Any]:
    return params() if callable(params) else dict(params)


def fetch_hot_ranking_frame(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if config.get("provider") != hithink_financial.SOURCE_ID:
        raise ValueError(f"未知热榜数据源: {config.get('provider')}")
    return hithink_financial.fetch_hot_ranking_frame(config)


__all__ = ["HOT_RANKINGS", "fetch_hot_ranking_frame", "resolve_params"]
