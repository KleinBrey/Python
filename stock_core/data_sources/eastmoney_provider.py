from __future__ import annotations

from typing import Any

import pandas as pd
import requests
from requests import RequestException


APP_ID = "appId01"
GLOBAL_ID = "786e4c21-70dc-435a-93bb-38"
REQUEST_TIMEOUT = 12

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://guba.eastmoney.com/rank/",
}


def _post_rank_list(url: str, payload: dict[str, Any]) -> pd.DataFrame:
    response = requests.post(url, json=payload, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get("data"):
        return pd.DataFrame()
    return pd.DataFrame(data["data"])


def _stock_secid(code: str) -> str:
    if code.startswith("SZ"):
        return f"0.{code[2:]}"
    if code.startswith("SH"):
        return f"1.{code[2:]}"
    return code


def _hk_secid(code: str) -> str:
    if "|" in code:
        code = code.split("|")[-1]
    if code.startswith("HK_"):
        code = code[3:]
    return f"116.{code}"


def _stock_code(code: str) -> str:
    if code.startswith(("SZ", "SH")):
        return code[2:]
    return code


def _hk_code(code: str) -> str:
    if "|" in code:
        code = code.split("|")[-1]
    if code.startswith("HK_"):
        code = code[3:]
    return code


def _fetch_quotes(secids: list[str]) -> pd.DataFrame:
    if not secids:
        return pd.DataFrame()

    params = {
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
        "fltt": "2",
        "invt": "2",
        "fields": "f14,f3,f12,f2",
        "secids": ",".join(secids),
    }
    response = requests.get(
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
        params=params,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json().get("data") or {}
    return pd.DataFrame(data.get("diff") or [])


def _merge_rank_and_quotes(
    rank_df: pd.DataFrame,
    code_column: str,
    secid_builder,
    code_builder,
    include_change_rank: bool = False,
) -> pd.DataFrame:
    if rank_df.empty:
        return pd.DataFrame()

    rank_df = rank_df.copy()
    rank_df["secid"] = rank_df[code_column].astype(str).map(secid_builder)
    rank_df["_merge_code"] = rank_df[code_column].astype(str).map(code_builder)
    try:
        quote_df = _fetch_quotes(rank_df["secid"].dropna().tolist())
    except RequestException as exc:
        print(f"东方财富行情接口调用失败，仅返回排名数据: {exc}")
        quote_df = pd.DataFrame()

    if quote_df.empty:
        result = pd.DataFrame()
        result["当前排名"] = pd.to_numeric(rank_df.get("rk"), errors="coerce")
        result["代码"] = rank_df["_merge_code"]
        result["股票名称"] = rank_df.get("n")
        result["最新价"] = None
        result["涨跌幅"] = None
        if include_change_rank:
            result["排名较昨日变动"] = pd.to_numeric(rank_df.get("hrc"), errors="coerce")
        return result

    quote_df = quote_df.rename(
        columns={
            "f2": "最新价",
            "f3": "涨跌幅",
            "f12": "行情代码",
            "f14": "股票名称",
        }
    )
    quote_df["_merge_code"] = quote_df["行情代码"].astype(str)

    result = rank_df.merge(quote_df, on="_merge_code", how="left")
    result["当前排名"] = pd.to_numeric(result.get("rk"), errors="coerce")
    result["代码"] = result["_merge_code"]
    result["最新价"] = pd.to_numeric(result.get("最新价"), errors="coerce")
    result["涨跌幅"] = pd.to_numeric(result.get("涨跌幅"), errors="coerce")
    result["涨跌额"] = result["最新价"] * result["涨跌幅"] / 100

    columns = ["当前排名", "代码", "股票名称", "最新价", "涨跌额", "涨跌幅"]
    if include_change_rank:
        result["排名较昨日变动"] = pd.to_numeric(result.get("hrc"), errors="coerce")
        columns = ["排名较昨日变动"] + columns
    return result[columns]


def fetch_stock_hot_rank(page_size: int = 100) -> pd.DataFrame:
    rank_df = _post_rank_list(
        "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
        {
            "appId": APP_ID,
            "globalId": GLOBAL_ID,
            "marketType": "",
            "pageNo": 1,
            "pageSize": page_size,
        },
    )
    return _merge_rank_and_quotes(rank_df, "sc", _stock_secid, _stock_code)


def fetch_stock_hot_up(page_size: int = 100) -> pd.DataFrame:
    rank_df = _post_rank_list(
        "https://emappdata.eastmoney.com/stockrank/getAllHisRcList",
        {
            "appId": APP_ID,
            "globalId": GLOBAL_ID,
            "marketType": "",
            "pageNo": 1,
            "pageSize": page_size,
        },
    )
    return _merge_rank_and_quotes(rank_df, "sc", _stock_secid, _stock_code, include_change_rank=True)


def fetch_hk_hot_rank(page_size: int = 100) -> pd.DataFrame:
    rank_df = _post_rank_list(
        "https://emappdata.eastmoney.com/stockrank/getAllCurrHkUsList",
        {
            "appId": APP_ID,
            "globalId": GLOBAL_ID,
            "marketType": "000003",
            "pageNo": 1,
            "pageSize": page_size,
        },
    )
    result = _merge_rank_and_quotes(rank_df, "sc", _hk_secid, _hk_code)
    if not result.empty:
        result = result[["当前排名", "代码", "股票名称", "最新价", "涨跌幅"]]
    return result


def fetch_hot_ranking_frame(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    params = dict(config.get("params") or {})
    page_size = int(params.get("pageSize", 100))
    function_name = config["function"]

    if function_name == "eastmoney_stock_hot_rank":
        return fetch_stock_hot_rank(page_size=page_size), params
    if function_name == "eastmoney_stock_hot_up":
        return fetch_stock_hot_up(page_size=page_size), params
    if function_name == "eastmoney_hk_hot_rank":
        return fetch_hk_hot_rank(page_size=page_size), params

    raise ValueError(f"未知东方财富榜单函数: {function_name}")
