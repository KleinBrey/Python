#!/usr/bin/env python3
"""同花顺扶摇 Financial API 直接调用案例。

准备：
    export HITHINK_FINANCE_API_KEY="你的 API Key"

运行全部案例：
    python examples/fuyao_api_example.py --symbol 600519.SH

只看历史日线：
    python examples/fuyao_api_example.py --symbol 000001.SZ --api history --days 60

脚本只使用 Python 标准库，展示最底层的 REST 调用方式。项目业务代码应继续通过
``data.providers.hithink_financial`` 和 ``data.service`` 使用统一数据格式。
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from zoneinfo import ZoneInfo

DEFAULT_BASE_URL = "https://fuyao.aicubes.cn"
SHANGHAI = ZoneInfo("Asia/Shanghai")
API_KEY = 'sk-fuyao-ubQXGmGz8oPFVwDZ1wITPlbyTtPJwErA'


class FuyaoApiError(RuntimeError):
    """扶摇 HTTP、认证或业务错误。"""


def normalize_symbol(value: str) -> str:
    text = value.strip().upper()
    if "." in text:
        code, exchange = text.split(".", 1)
    else:
        code = text
        if code.startswith(("4", "8", "92")):
            exchange = "BJ"
        elif code.startswith(("5", "6", "9")):
            exchange = "SH"
        else:
            exchange = "SZ"
    if len(code) != 6 or not code.isdigit() or exchange not in {"SH", "SZ", "BJ"}:
        raise ValueError("symbol 必须是 A 股代码，例如 600519.SH 或 000001.SZ")
    return f"{code}.{exchange}"


def timestamp_ms(value: datetime) -> int:
    return int(value.astimezone(SHANGHAI).timestamp() * 1000)


def build_ssl_context() -> ssl.SSLContext:
    """选择可用 CA 文件，始终保留 HTTPS 证书校验。"""

    candidates = [os.getenv("SSL_CERT_FILE", "")]
    try:
        import certifi

        candidates.append(certifi.where())
    except ImportError:
        pass
    default_paths = ssl.get_default_verify_paths()
    candidates.extend(
        [
            default_paths.cafile or "",
            "/etc/ssl/cert.pem",
            "/opt/homebrew/etc/openssl@3/cert.pem",
            "/opt/homebrew/etc/ca-certificates/cert.pem",
        ]
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


def request_api(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    timeout: int = 30,
) -> dict[str, Any]:
    """发送 GET 请求并拆开扶摇统一 ApiResponse 信封。"""

    api_key = os.getenv("HITHINK_FINANCE_API_KEY", API_KEY).strip()
    if not api_key:
        raise FuyaoApiError(
            "未配置 HITHINK_FINANCE_API_KEY；请先从扶摇 API Key 管理页创建并导出"
        )
    base_url = os.getenv("HITHINK_FINANCE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    query = urllib.parse.urlencode(
        {key: value for key, value in (params or {}).items() if value is not None}
    )
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "X-api-key": api_key,
            "Accept": "application/json",
            "User-Agent": "stock-fuyao-example/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=build_ssl_context(),
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise FuyaoApiError(f"HTTP {exc.code}: {detail[:300]}") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            raise FuyaoApiError(
                "SSL 证书校验失败；请安装 certifi 或通过 SSL_CERT_FILE 指定 CA 文件"
            ) from exc
        raise FuyaoApiError(f"网络连接失败: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise FuyaoApiError("接口返回的内容不是有效 JSON") from exc

    if not isinstance(payload, dict):
        raise FuyaoApiError("接口响应不是 JSON 对象")
    if payload.get("code") != 0:
        request_id = payload.get("request_id")
        request_suffix = f"，request_id={request_id}" if request_id else ""
        raise FuyaoApiError(
            f"业务错误 code={payload.get('code')}: {payload.get('message')}{request_suffix}"
        )
    data = payload.get("data")
    if not isinstance(data, dict):
        raise FuyaoApiError("成功响应缺少 data 对象")
    return data


def print_json(title: str, value: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def ticker_search_case(symbol: str) -> None:
    data = request_api(
        "/api/meta/tickers/search",
        {"q": symbol, "asset_type": "a-share", "limit": 10},
    )
    print_json("1. 标的检索", data)


def snapshot_case(symbol: str) -> None:
    data = request_api(
        "/api/a-share/prices/snapshot",
        {"thscodes": symbol},
    )
    print_json("2. 最新行情快照", data)


def history_case(symbol: str, days: int) -> None:
    end = datetime.now(SHANGHAI)
    start = end - timedelta(days=days)
    data = request_api(
        "/api/a-share/prices/historical",
        {
            "thscode": symbol,
            "interval": "1d",
            "start": timestamp_ms(start.replace(hour=0, minute=0, second=0, microsecond=0)),
            "end": timestamp_ms(end.replace(hour=23, minute=59, second=59, microsecond=999000)),
            "adjust": "forward",
            "offset": 0,
        },
    )
    rows = sorted(data.get("item") or [], key=lambda item: item.get("date_ms") or 0)
    print_json(
        "3. 前复权历史日线（只展示最后 5 根）",
        {
            "timestamp": data.get("timestamp"),
            "row_count": len(rows),
            "item": rows[-5:],
        },
    )


def valuation_case(symbol: str) -> None:
    data = request_api(
        "/api/a-share/valuations/snapshot",
        {"thscodes": symbol},
    )
    print_json("4. 最新估值", data)


def hot_list_case() -> None:
    data = request_api(
        "/api/a-share/special-data/hot-stock-list",
        {"period": "day"},
    )
    rows = data.get("item") or []
    print_json(
        "5. 同花顺 24 小时热股榜（只展示前 10 名）",
        {
            "timestamp": data.get("timestamp"),
            "item": rows[:10],
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="直接调用同花顺扶摇 Financial API")
    parser.add_argument(
        "--symbol",
        default="600519.SH",
        help="A 股 thscode，例如 600519.SH、000001.SZ",
    )
    parser.add_argument(
        "--api",
        choices=("all", "search", "snapshot", "history", "valuation", "hot"),
        default="all",
        help="只运行指定接口案例，默认 all",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="历史日线回溯自然日数量，默认 30",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        symbol = normalize_symbol(args.symbol)
        days = max(1, min(3650, args.days))
        cases = {
            "search": lambda: ticker_search_case(symbol),
            "snapshot": lambda: snapshot_case(symbol),
            "history": lambda: history_case(symbol, days),
            "valuation": lambda: valuation_case(symbol),
            "hot": hot_list_case,
        }
        selected = list(cases) if args.api == "all" else [args.api]
        failed = False
        for case_name in selected:
            try:
                cases[case_name]()
            except FuyaoApiError as exc:
                failed = True
                print(f"\n[{case_name}] 调用失败：{exc}", file=sys.stderr)
        return 1 if failed else 0
    except (ValueError, FuyaoApiError) as exc:
        print(f"调用失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
