from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import akshare as ak
import pandas as pd


def today_yyyymmdd() -> str:
    return datetime.today().strftime("%Y%m%d")


HOT_RANKINGS: list[dict[str, Any]] = [
    {
        "id": "xq-follow-hot",
        "title": "雪球关注榜",
        "source": "雪球",
        "description": "沪深股市关注排行榜",
        "function": "stock_hot_follow_xq",
        "params": {"symbol": "最热门"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "xq-follow-week",
        "title": "雪球本周新增关注",
        "source": "雪球",
        "description": "沪深股市本周新增关注排行榜",
        "function": "stock_hot_follow_xq",
        "params": {"symbol": "本周新增"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "xq-tweet-hot",
        "title": "雪球讨论榜",
        "source": "雪球",
        "description": "沪深股市讨论排行榜",
        "function": "stock_hot_tweet_xq",
        "params": {"symbol": "最热门"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "xq-deal-hot",
        "title": "雪球交易分享榜",
        "source": "雪球",
        "description": "沪深股市分享交易排行榜",
        "function": "stock_hot_deal_xq",
        "params": {"symbol": "最热门"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "em-rank",
        "title": "东财人气榜",
        "source": "东方财富",
        "description": "东方财富个股人气榜",
        "function": "stock_hot_rank_em",
        "params": {},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "em-up",
        "title": "东财飙升榜",
        "source": "东方财富",
        "description": "东方财富个股人气飙升榜",
        "function": "stock_hot_up_em",
        "params": {},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "em-hk-rank",
        "title": "东财港股人气榜",
        "source": "东方财富",
        "description": "东方财富港股市场人气榜",
        "function": "stock_hk_hot_rank_em",
        "params": {},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id265",
    },
    {
        "id": "baidu-a",
        "title": "百度热搜 A股",
        "source": "百度股市通",
        "description": "百度股市通 A 股热搜股票",
        "function": "stock_hot_search_baidu",
        "params": lambda: {"symbol": "A股", "date": today_yyyymmdd(), "time": "今日"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id274",
    },
    {
        "id": "baidu-hk",
        "title": "百度热搜 港股",
        "source": "百度股市通",
        "description": "百度股市通港股热搜股票",
        "function": "stock_hot_search_baidu",
        "params": lambda: {"symbol": "港股", "date": today_yyyymmdd(), "time": "今日"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id274",
    },
    {
        "id": "baidu-us",
        "title": "百度热搜 美股",
        "source": "百度股市通",
        "description": "百度股市通美股热搜股票",
        "function": "stock_hot_search_baidu",
        "params": lambda: {"symbol": "美股", "date": today_yyyymmdd(), "time": "今日"},
        "docUrl": "https://akshare.akfamily.xyz/data/stock/stock.html#id274",
    },
]


def resolve_params(params: dict[str, Any] | Callable[[], dict[str, Any]]) -> dict[str, Any]:
    return params() if callable(params) else dict(params)


def fetch_hot_ranking_frame(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    params = resolve_params(config["params"])
    func = getattr(ak, config["function"])
    return func(**params), params
