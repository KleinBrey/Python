"""同花顺扶摇官方 Financial API 适配器。

系统内的结构化证券数据统一从本模块进入。供应商字段只在这里出现，
业务、策略、存储和前端继续使用项目自己的稳定数据契约。
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import lru_cache
import json
import math
from threading import RLock
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from data.normalizers import normalize_market_bars, normalize_stock_master, normalize_symbol
from data.providers.iwencai_api import build_ssl_context
from data.settings import get_setting


SOURCE_ID = "hithink-financial"
SOURCE_NAME = "同花顺扶摇 Financial API"
DEFAULT_BASE_URL = "https://fuyao.aicubes.cn"
DOCS_URL = "https://fuyao.aicubes.cn/docs/"
_SHANGHAI = ZoneInfo("Asia/Shanghai")
_HISTORY_BAR_CACHE: dict[
    tuple[str, str, str, str],
    tuple[float, pd.DataFrame],
] = {}
_HISTORY_BAR_INFLIGHT: dict[
    tuple[str, str, str, str],
    Future[pd.DataFrame],
] = {}
_HISTORY_BAR_CACHE_LOCK = RLock()


class HiThinkFinancialError(RuntimeError):
    """扶摇 API 的认证、网络或业务错误。"""


def _setting(name: str, default: str = "") -> str:
    return get_setting(name, default)


def is_configured() -> bool:
    api_key = _setting("HITHINK_FINANCE_API_KEY")
    return bool(api_key and "*" not in api_key and "\\" not in api_key)


def _request(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    timeout: int = 60,
) -> dict[str, Any]:
    api_key = _setting("HITHINK_FINANCE_API_KEY")
    if not api_key:
        raise HiThinkFinancialError("未配置 HITHINK_FINANCE_API_KEY")
    if "*" in api_key or "\\" in api_key:
        raise HiThinkFinancialError("HITHINK_FINANCE_API_KEY 看起来仍是脱敏值")

    query = urllib.parse.urlencode(
        {key: value for key, value in (params or {}).items() if value is not None}
    )
    url = f"{_setting('HITHINK_FINANCE_BASE_URL', DEFAULT_BASE_URL).rstrip('/')}{path}"
    if query:
        url = f"{url}?{query}"
    request = urllib.request.Request(url, headers={"X-api-key": api_key}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=build_ssl_context()) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HiThinkFinancialError(f"扶摇 API 返回 HTTP {exc.code}: {detail[:300]}") from exc
    except urllib.error.URLError as exc:
        raise HiThinkFinancialError(f"扶摇 API 网络连接失败: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise HiThinkFinancialError("扶摇 API 返回了无法解析的 JSON") from exc

    if not isinstance(payload, dict) or payload.get("code") != 0:
        message = payload.get("message", "响应格式异常") if isinstance(payload, dict) else "响应格式异常"
        request_id = payload.get("request_id") if isinstance(payload, dict) else None
        suffix = f" (request_id={request_id})" if request_id else ""
        raise HiThinkFinancialError(f"扶摇 API 请求失败: {message}{suffix}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise HiThinkFinancialError("扶摇 API 成功响应缺少 data 对象")
    return data


def _timestamp_ms(value: str, *, end_of_day: bool = False) -> int:
    parsed = datetime.strptime(value, "%Y%m%d").replace(tzinfo=_SHANGHAI)
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=999000)
    return int(parsed.timestamp() * 1000)


def _history_cache_ttl() -> int:
    try:
        value = int(_setting("HITHINK_HISTORY_CACHE_TTL", "1800"))
    except ValueError:
        value = 1800
    return max(0, min(3600, value))


def _cached_history_bars(
    symbol: str,
    start_date: str,
    end_date: str,
    adjustment: str,
) -> pd.DataFrame:
    key = (symbol, start_date, end_date, adjustment)
    now = time.monotonic()
    ttl = _history_cache_ttl()
    with _HISTORY_BAR_CACHE_LOCK:
        cached = _HISTORY_BAR_CACHE.get(key)
        if cached and now - cached[0] <= ttl:
            return cached[1].copy(deep=True)
        future = _HISTORY_BAR_INFLIGHT.get(key)
        owns_request = future is None
        if future is None:
            future = Future()
            _HISTORY_BAR_INFLIGHT[key] = future

    if not owns_request:
        return future.result().copy(deep=True)

    try:
        frame = fetch_daily_bars(
            symbol,
            start_date,
            end_date,
            adjustment=adjustment,
        )
        with _HISTORY_BAR_CACHE_LOCK:
            if ttl:
                _HISTORY_BAR_CACHE[key] = (time.monotonic(), frame.copy(deep=True))
                if len(_HISTORY_BAR_CACHE) > 512:
                    oldest_key = min(
                        _HISTORY_BAR_CACHE,
                        key=lambda item: _HISTORY_BAR_CACHE[item][0],
                    )
                    _HISTORY_BAR_CACHE.pop(oldest_key, None)
            future.set_result(frame.copy(deep=True))
        return frame
    except BaseException as exc:
        future.set_exception(exc)
        raise
    finally:
        with _HISTORY_BAR_CACHE_LOCK:
            if _HISTORY_BAR_INFLIGHT.get(key) is future:
                _HISTORY_BAR_INFLIGHT.pop(key, None)


def _symbols(values: str | Iterable[str]) -> list[str]:
    raw_values = values.split(",") if isinstance(values, str) else values
    result: list[str] = []
    seen: set[str] = set()
    for value in raw_values:
        text = str(value).strip()
        if not text:
            continue
        symbol = normalize_symbol(text)[0]
        if symbol not in seen:
            result.append(symbol)
            seen.add(symbol)
    return result


def _batches(values: list[str], size: int) -> Iterator[list[str]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def check_connection(*, timeout: int = 15) -> dict[str, Any]:
    data = _request(
        "/api/meta/tickers/list",
        {"asset_type": "a-share", "limit": 1, "offset": 0},
        timeout=timeout,
    )
    return {
        "ok": True,
        "message": f"官方接口可用，代码表返回 {len(data.get('item') or [])} 条探测记录",
        "timestamp": data.get("timestamp"),
    }


def fetch_ticker_list(
    *,
    asset_type: str = "a-share",
    page_size: int = 10_000,
    timeout: int = 60,
) -> pd.DataFrame:
    if not 1 <= page_size <= 10_000:
        raise ValueError("page_size 必须在 1..10000")
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        data = _request(
            "/api/meta/tickers/list",
            {"asset_type": asset_type, "limit": page_size, "offset": offset},
            timeout=timeout,
        )
        page = [item for item in (data.get("item") or []) if isinstance(item, dict)]
        rows.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return pd.DataFrame(rows)


def search_tickers(
    query: str,
    *,
    asset_type: str = "a-share",
    exchange: str | None = None,
    limit: int = 10,
    timeout: int = 30,
) -> pd.DataFrame:
    if not query.strip():
        raise ValueError("query 不能为空")
    data = _request(
        "/api/meta/tickers/search",
        {
            "q": query.strip(),
            "asset_type": asset_type,
            "exchange": exchange,
            "limit": max(1, min(50, limit)),
        },
        timeout=timeout,
    )
    return pd.DataFrame(data.get("item") or [])


def fetch_price_snapshot(
    symbols: str | Iterable[str] | None = None,
    *,
    page_size: int = 1000,
    timeout: int = 60,
) -> pd.DataFrame:
    if symbols is not None:
        normalized = _symbols(symbols)
        if not normalized:
            return pd.DataFrame()
        pages = []
        for batch in _batches(normalized, 100):
            data = _request(
                "/api/a-share/prices/snapshot",
                {"thscodes": ",".join(batch)},
                timeout=timeout,
            )
            pages.extend(data.get("item") or [])
        return pd.DataFrame(pages)

    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        data = _request(
            "/api/a-share/prices/snapshot",
            {"limit": page_size, "offset": offset},
            timeout=timeout,
        )
        page = [item for item in (data.get("item") or []) if isinstance(item, dict)]
        rows.extend(page)
        total = int(data.get("total") or 0)
        offset += len(page)
        if not page or offset >= total:
            break
    return pd.DataFrame(rows)


def fetch_valuation_snapshot(
    symbols: str | Iterable[str],
    *,
    timeout: int = 60,
) -> pd.DataFrame:
    normalized = _symbols(symbols)
    rows: list[dict[str, Any]] = []
    for batch in _batches(normalized, 100):
        data = _request(
            "/api/a-share/valuations/snapshot",
            {"thscodes": ",".join(batch)},
            timeout=timeout,
        )
        rows.extend(data.get("item") or [])
    return pd.DataFrame(rows)


def fetch_trading_days(*, timeout: int = 30) -> pd.DataFrame:
    data = _request("/api/a-share/calendar/trading-days", timeout=timeout)
    return pd.DataFrame(data.get("item") or [])


def fetch_financial_statements(
    symbol: str,
    statement: str,
    *,
    period: str = "annual",
    limit: int = 4,
    start_date: str | None = None,
    end_date: str | None = None,
    timeout: int = 60,
) -> pd.DataFrame:
    """获取利润表、资产负债表或现金流量表的官方多期序列。"""

    paths = {
        "income": "/api/a-share/financials/income-statements",
        "balance": "/api/a-share/financials/balance-sheets",
        "cash-flow": "/api/a-share/financials/cash-flow-statements",
    }
    if statement not in paths:
        raise ValueError("statement 仅支持 income、balance、cash-flow")
    if period not in {"annual", "quarterly"}:
        raise ValueError("period 仅支持 annual、quarterly")
    if (start_date is None) != (end_date is None):
        raise ValueError("start_date 与 end_date 必须同时提供")

    params: dict[str, Any] = {
        "thscode": normalize_symbol(symbol)[0],
        "period": period,
    }
    if start_date is not None and end_date is not None:
        params.update(
            {
                "start": _timestamp_ms(start_date),
                "end": _timestamp_ms(end_date, end_of_day=True),
            }
        )
    else:
        params["limit"] = max(1, min(20, limit))
    data = _request(paths[statement], params, timeout=timeout)
    return pd.DataFrame(data.get("item") or [])


def fetch_financial_indicators(
    symbol: str,
    report: str,
    *,
    timeout: int = 60,
) -> pd.DataFrame:
    """将扶摇五类财务能力指标展开为一行宽表。"""

    data = _request(
        "/api/a-share/financials/indicators",
        {"thscode": normalize_symbol(symbol)[0], "report": report},
        timeout=timeout,
    )
    row: dict[str, Any] = {
        "thscode": data.get("thscode"),
        "report": data.get("report"),
    }
    for ability in data.get("abilities") or []:
        if not isinstance(ability, dict):
            continue
        for indicator in ability.get("indicators") or []:
            if not isinstance(indicator, dict) or not indicator.get("index_id"):
                continue
            row[str(indicator["index_id"])] = pd.to_numeric(
                indicator.get("value"),
                errors="coerce",
            )
    return pd.DataFrame([row])


def fetch_stock_master(
    *,
    include_valuations: bool = True,
    timeout: int = 60,
) -> pd.DataFrame:
    """返回系统股票主数据。

    扶摇当前代码表不提供行业、上市状态、总股本和总市值；这些统一列保留为空。
    可用的官方 PB 估值会合并到 ``pb``。
    """

    tickers = fetch_ticker_list(asset_type="a-share", timeout=timeout)
    if tickers.empty:
        return normalize_stock_master(
            tickers,
            source=SOURCE_ID,
            column_map={},
        )

    if include_valuations:
        valuations = fetch_valuation_snapshot(tickers["thscode"].tolist(), timeout=timeout)
        if not valuations.empty:
            tickers = tickers.merge(
                valuations[["thscode", "pb_mrq"]],
                on="thscode",
                how="left",
            )
    return normalize_stock_master(
        tickers,
        source=SOURCE_ID,
        column_map={
            "thscode": "symbol",
            "name": "name",
            "pb_mrq": "pb",
        },
    )


def fetch_daily_bars(
    symbol: str,
    start_date: str,
    end_date: str,
    *,
    adjustment: str = "qfq",
    timeout: int = 60,
) -> pd.DataFrame:
    if adjustment not in {"none", "qfq", "hfq"}:
        raise ValueError("adjustment 仅支持 none、qfq、hfq")
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    if start > end:
        raise ValueError("start_date 不能晚于 end_date")
    if (end - start).days > 3660:
        raise ValueError("扶摇历史 K 线单次查询跨度不能超过 10 年")

    normalized_symbol = normalize_symbol(symbol)[0]
    api_adjustment = {"none": "none", "qfq": "forward", "hfq": "backward"}[adjustment]
    data = _request(
        "/api/a-share/prices/historical",
        {
            "thscode": normalized_symbol,
            "interval": "1d",
            "start": _timestamp_ms(start_date),
            "end": _timestamp_ms(end_date, end_of_day=True),
            "adjust": api_adjustment,
            "offset": 0,
        },
        timeout=timeout,
    )
    frame = pd.DataFrame(data.get("item") or [])
    if frame.empty:
        return normalize_market_bars(
            frame,
            source=SOURCE_ID,
            column_map={},
            adjustment=adjustment,
        )
    frame["symbol"] = normalized_symbol
    frame["trade_date"] = (
        pd.to_datetime(frame["date_ms"], unit="ms", utc=True)
        .dt.tz_convert(_SHANGHAI)
        .dt.tz_localize(None)
    )
    return normalize_market_bars(
        frame,
        source=SOURCE_ID,
        column_map={
            "symbol": "symbol",
            "trade_date": "trade_date",
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "close_price": "close",
            "volume": "volume",
            "turnover": "amount",
        },
        adjustment=adjustment,
    )


def _aggregate_history_rows(rows: list[dict[str, Any]], period: str) -> list[dict[str, Any]]:
    if period == "daily":
        return rows
    groups: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        parsed = datetime.strptime(row["date"], "%Y-%m-%d").date()
        if period == "weekly":
            iso_year, iso_week, _ = parsed.isocalendar()
            key = (iso_year, iso_week)
        else:
            key = (parsed.year, parsed.month)
        groups[key].append(row)

    result = []
    for key in sorted(groups):
        group = groups[key]
        previous_close = group[0].get("preClose")
        result.append(
            {
                "date": group[-1]["date"],
                "open": group[0]["open"],
                "close": group[-1]["close"],
                "low": min(row["low"] for row in group),
                "high": max(row["high"] for row in group),
                "volume": sum(row["volume"] for row in group),
                "amount": sum(row.get("amount") or 0 for row in group),
                "changePct": (
                    ((group[-1]["close"] / previous_close) - 1) * 100
                    if previous_close not in (None, 0)
                    else None
                ),
                "turnover": None,
            }
        )
    return result


@lru_cache(maxsize=256)
def _ticker_name(symbol: str) -> str | None:
    frame = search_tickers(symbol, limit=10)
    if frame.empty:
        return None
    exact = frame[frame["thscode"].astype(str).str.upper() == symbol.upper()]
    row = exact.iloc[0] if not exact.empty else frame.iloc[0]
    return str(row.get("name") or "") or None


def prefetch_stock_histories(
    symbols: str | Iterable[str],
    start_date: str,
    end_date: str,
    *,
    adjust: str = "none",
    workers: int | None = None,
) -> dict[str, Any]:
    """有限并发预取筛选结果的日线，供日/周/月图表共同复用。"""

    normalized = _symbols(symbols)
    if len(normalized) > 300:
        raise ValueError("单次最多预缓存 300 只股票")
    if adjust not in {"none", "qfq", "hfq"}:
        raise ValueError("adjust 仅支持 none、qfq、hfq")
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    if start > end:
        raise ValueError("start_date 不能晚于 end_date")
    if not normalized:
        return {
            "requested": 0,
            "completed": 0,
            "failed": 0,
            "rowCount": 0,
            "errors": [],
        }
    if not is_configured():
        return {
            "requested": len(normalized),
            "completed": 0,
            "failed": len(normalized),
            "rowCount": 0,
            "errors": ["未配置 HITHINK_FINANCE_API_KEY"],
        }

    if workers is None:
        try:
            workers = int(_setting("HITHINK_PREFETCH_WORKERS", "4"))
        except ValueError:
            workers = 4
    worker_count = max(1, min(8, workers))
    completed = 0
    row_count = 0
    errors: list[str] = []

    with ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="hithink-history",
    ) as executor:
        futures = {
            executor.submit(
                _cached_history_bars,
                symbol,
                start_date,
                end_date,
                adjust,
            ): symbol
            for symbol in normalized
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                frame = future.result()
                completed += 1
                row_count += len(frame)
            except Exception as exc:
                if len(errors) < 10:
                    errors.append(f"{symbol}: {exc}")

    return {
        "requested": len(normalized),
        "completed": completed,
        "failed": len(normalized) - completed,
        "rowCount": row_count,
        "workers": worker_count,
        "errors": errors,
    }


def fetch_stock_history(
    symbol: str,
    period: str,
    start_date: str,
    end_date: str,
    adjust: str = "none",
    name: str | None = None,
) -> dict[str, Any]:
    """为前端 TradingView K 线组件返回稳定的历史行情 JSON。"""

    if period not in {"daily", "weekly", "monthly"}:
        raise ValueError("period 仅支持 daily、weekly、monthly")
    if adjust not in {"none", "qfq", "hfq"}:
        raise ValueError("adjust 仅支持 none、qfq、hfq")
    normalized_symbol, code, _exchange = normalize_symbol(symbol)
    frame = _cached_history_bars(
        normalized_symbol,
        start_date,
        end_date,
        adjust,
    )
    raw_rows: list[dict[str, Any]] = []
    previous_close: float | None = None
    for row in frame.to_dict(orient="records"):
        close = float(row["close"])
        raw_rows.append(
            {
                "date": row["trade_date"],
                "open": float(row["open"]),
                "close": close,
                "low": float(row["low"]),
                "high": float(row["high"]),
                "volume": float(row["volume"]),
                "amount": None if pd.isna(row["amount"]) else float(row["amount"]),
                "changePct": (
                    ((close / previous_close) - 1) * 100
                    if previous_close not in (None, 0)
                    else None
                ),
                "turnover": None,
                "preClose": previous_close,
            }
        )
        previous_close = close

    rows = _aggregate_history_rows(raw_rows, period)
    for row in rows:
        row.pop("preClose", None)
        if row["changePct"] is not None and not math.isfinite(row["changePct"]):
            row["changePct"] = None
    adjust_labels = {"none": "不复权", "qfq": "前复权", "hfq": "后复权"}
    return {
        "symbol": code,
        "thscode": normalized_symbol,
        "name": name.strip() if name and name.strip() else _ticker_name(normalized_symbol),
        "period": period,
        "adjust": adjust,
        "adjustLabel": adjust_labels[adjust],
        "dates": [row["date"] for row in rows],
        "candles": [[row["open"], row["close"], row["low"], row["high"]] for row in rows],
        "volumes": [row["volume"] for row in rows],
        "rows": rows,
        "updatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dataSource": SOURCE_NAME,
        "sourceUrl": DOCS_URL,
    }


def fetch_hot_ranking_frame(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = str(config.get("endpoint") or "").strip()
    if path not in {
        "/api/a-share/special-data/skyrocket-list",
        "/api/a-share/special-data/hot-stock-list",
        "/api/a-share/special-data/limit-up-pool",
    }:
        raise ValueError(f"不支持的扶摇热榜接口: {path}")
    params = dict(config.get("params") or {})
    data = _request(path, params)
    frame = pd.DataFrame(data.get("item") or [])
    if not frame.empty:
        frame["provider"] = SOURCE_ID
    return frame, params


__all__ = [
    "DOCS_URL",
    "HiThinkFinancialError",
    "SOURCE_ID",
    "SOURCE_NAME",
    "check_connection",
    "fetch_daily_bars",
    "fetch_financial_indicators",
    "fetch_financial_statements",
    "fetch_hot_ranking_frame",
    "fetch_price_snapshot",
    "prefetch_stock_histories",
    "fetch_stock_history",
    "fetch_stock_master",
    "fetch_ticker_list",
    "fetch_trading_days",
    "fetch_valuation_snapshot",
    "is_configured",
    "search_tickers",
]
