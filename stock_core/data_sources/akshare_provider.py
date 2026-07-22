from __future__ import annotations

from typing import Any, Callable

import akshare as ak
import pandas as pd


def today_yyyymmdd() -> str:
    return datetime.today().strftime("%Y%m%d")


def resolve_params(params: dict[str, Any] | Callable[[], dict[str, Any]]) -> dict[str, Any]:
    return params() if callable(params) else dict(params)


def fetch_hot_ranking_frame(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    params = resolve_params(config["params"])
    func = getattr(ak, config["function"])
    return func(**params), params
