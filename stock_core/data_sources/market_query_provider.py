"""同花顺问财行情查询适配器，用于个股历史 K 线。"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from functools import lru_cache
import json
import math
import re
import secrets
import urllib.error
import urllib.request
from typing import Any

from stock_core.data_sources.iwencai_provider import (
    DEFAULT_BASE_URL,
    build_ssl_context,
    get_setting,
)


SKILL_ID = "hithink-market-query"
SKILL_VERSION = "1.0.0"
SOURCE_NAME = "同花顺问财"
SOURCE_URL = "https://www.iwencai.com/unifiedwap/chat"
FIELD_PATTERN = re.compile(r"^(开盘价|收盘价|最高价|最低价|成交量)\[(\d{8})\]$")


class MarketQueryError(RuntimeError):
    pass


def normalize_a_share_symbol(value: str) -> str:
    match = re.search(r"(?<!\d)(\d{6})(?!\d)", str(value or ""))
    if not match:
        raise ValueError("股票代码必须包含 6 位数字")
    return match.group(1)


def _number(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        number = float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _query_date(value: str) -> str:
    parsed = datetime.strptime(value, "%Y%m%d")
    return f"{parsed.year}年{parsed.month}月{parsed.day}日"


def _build_query(code: str, start_date: str, end_date: str, *, relaxed: bool = False) -> str:
    date_range = f"{_query_date(start_date)}至{_query_date(end_date)}"
    prefix = f"股票代码{code}" if relaxed else code
    return f"{prefix}，{date_range}，每日开盘价、收盘价、最高价、最低价、成交量"


def _request_history(query: str, *, call_type: str, timeout: int = 60) -> dict[str, Any]:
    api_key = get_setting("IWENCAI_API_KEY")
    if not api_key:
        raise MarketQueryError("未配置 IWENCAI_API_KEY")
    if "*" in api_key or "\\" in api_key:
        raise MarketQueryError("IWENCAI_API_KEY 看起来仍是脱敏值")

    trace_id = secrets.token_hex(32)
    payload = {
        "query": query,
        "page": "1",
        "limit": "10",
        "is_cache": "1",
        "expand_index": "true",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Claw-Call-Type": call_type,
        "X-Claw-Skill-Id": SKILL_ID,
        "X-Claw-Skill-Version": SKILL_VERSION,
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": trace_id,
    }
    base_url = get_setting("IWENCAI_BASE_URL", DEFAULT_BASE_URL)
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/query2data",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=build_ssl_context(),
        ) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise MarketQueryError("IWENCAI_API_KEY 无效或已过期") from exc
        raise MarketQueryError(f"问财行情接口返回 HTTP {exc.code}：{detail[:300]}") from exc
    except urllib.error.URLError as exc:
        raise MarketQueryError(f"问财行情网络连接失败：{exc.reason}") from exc

    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        raise MarketQueryError(f"问财行情返回了无法解析的内容：{body[:300]}") from exc
    if not isinstance(result, dict):
        raise MarketQueryError("问财行情返回格式异常")
    result["trace_id"] = trace_id
    return result


def _select_stock_item(result: dict[str, Any], code: str) -> dict[str, Any] | None:
    rows = result.get("datas") or []
    if not isinstance(rows, list):
        raise MarketQueryError("问财行情 datas 字段不是列表")
    candidates = [item for item in rows if isinstance(item, dict)]
    for item in candidates:
        try:
            if normalize_a_share_symbol(item.get("股票代码", "")) == code:
                return item
        except ValueError:
            continue
    return candidates[0] if len(candidates) == 1 else None


def _parse_daily_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    values_by_date: dict[str, dict[str, float]] = defaultdict(dict)
    field_names = {
        "开盘价": "open",
        "收盘价": "close",
        "最高价": "high",
        "最低价": "low",
        "成交量": "volume",
    }
    for key, raw_value in item.items():
        match = FIELD_PATTERN.fullmatch(str(key))
        if not match:
            continue
        number = _number(raw_value)
        if number is not None:
            values_by_date[match.group(2)][field_names[match.group(1)]] = number

    rows: list[dict[str, Any]] = []
    for raw_date in sorted(values_by_date):
        values = values_by_date[raw_date]
        if not all(field in values for field in ("open", "close", "low", "high")):
            continue
        rows.append(
            {
                "date": datetime.strptime(raw_date, "%Y%m%d").date().isoformat(),
                "open": values["open"],
                "close": values["close"],
                "low": values["low"],
                "high": values["high"],
                "volume": values.get("volume", 0),
                "amount": 0,
                "changePct": None,
                "turnover": None,
            }
        )
    return rows


def _aggregate_rows(rows: list[dict[str, Any]], period: str) -> list[dict[str, Any]]:
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

    aggregated: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        aggregated.append(
            {
                "date": group[-1]["date"],
                "open": group[0]["open"],
                "close": group[-1]["close"],
                "low": min(row["low"] for row in group),
                "high": max(row["high"] for row in group),
                "volume": sum(row["volume"] for row in group),
                "amount": 0,
                "changePct": None,
                "turnover": None,
            }
        )
    return aggregated


@lru_cache(maxsize=64)
def _fetch_daily_history(
    code: str,
    start_date: str,
    end_date: str,
) -> tuple[str | None, list[dict[str, Any]], str]:
    query = _build_query(code, start_date, end_date)
    result = _request_history(query, call_type="normal")
    item = _select_stock_item(result, code)
    daily_rows = _parse_daily_rows(item or {})

    if not daily_rows:
        query = _build_query(code, start_date, end_date, relaxed=True)
        result = _request_history(query, call_type="retry")
        item = _select_stock_item(result, code)
        daily_rows = _parse_daily_rows(item or {})
    if not daily_rows:
        raise MarketQueryError(
            "同花顺问财未返回可解析的历史行情，可到问财 Web 端确认该股票和日期区间"
        )

    return item.get("股票简称") if item else None, daily_rows, query


def fetch_stock_history(
    symbol: str,
    period: str,
    start_date: str,
    end_date: str,
    adjust: str = "none",
) -> dict[str, Any]:
    """通过 hithink-market-query 获取并标准化 A 股历史行情。"""

    code = normalize_a_share_symbol(symbol)
    if period not in {"daily", "weekly", "monthly"}:
        raise ValueError("period 仅支持 daily、weekly、monthly")
    if adjust not in {"", "none"}:
        raise ValueError("同花顺问财历史行情当前仅支持不复权数据")
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    if start > end:
        raise ValueError("startDate 不能晚于 endDate")

    name, daily_rows, query = _fetch_daily_history(code, start_date, end_date)

    rows = _aggregate_rows(daily_rows, period)
    return {
        "symbol": code,
        "name": name,
        "period": period,
        "adjust": "none",
        "adjustLabel": "不复权",
        "dates": [row["date"] for row in rows],
        "candles": [[row["open"], row["close"], row["low"], row["high"]] for row in rows],
        "volumes": [row["volume"] for row in rows],
        "rows": rows,
        "query": query,
        "updatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dataSource": SOURCE_NAME,
        "sourceUrl": SOURCE_URL,
    }
