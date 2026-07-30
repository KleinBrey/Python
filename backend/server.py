from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.hot_rankings import HOT_RANKINGS, fetch_hot_ranking_frame, resolve_params  # noqa: E402
from data.providers import hithink_financial  # noqa: E402
from data.providers import iwencai_api as iwencai_provider  # noqa: E402
from data.providers.hithink_financial import fetch_stock_history  # noqa: E402
from stock_core.database import collections as database  # noqa: E402
from stock_core.strategies.sources import load_strategy_sources  # noqa: E402
from data.registry import list_sources  # noqa: E402

RANKING_BY_ID = {item["id"]: item for item in HOT_RANKINGS}


class DatabaseUnavailable(RuntimeError):
    pass


def to_jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "item"):
        return to_jsonable(value.item())
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items() if key != "_id"}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def dataframe_records(df: pd.DataFrame, limit: int = 200) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    head = df.head(limit)
    clean = head.where(pd.notnull(head), None)
    return [to_jsonable(record) for record in clean.to_dict(orient="records")]


def parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "y", "on"}


def parse_int(value: str | None, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value) if value is not None else default
    except ValueError:
        parsed = default
    return max(minimum, min(maximum, parsed))


def resolve_history_dates(
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[str, str]:
    default_history_days = parse_int(
        os.getenv("HISTORY_DEFAULT_DAYS"),
        default=550,
        minimum=60,
        maximum=3650,
    )
    resolved_end = end_date or datetime.now().strftime("%Y%m%d")
    resolved_start = start_date or (
        datetime.now() - timedelta(days=default_history_days)
    ).strftime("%Y%m%d")
    for value, label in ((resolved_start, "startDate"), (resolved_end, "endDate")):
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as exc:
            raise ValueError(f"{label} 必须是 YYYYMMDD 格式") from exc
    if resolved_start > resolved_end:
        raise ValueError("startDate 不能晚于 endDate")
    return resolved_start, resolved_end


def mongo_available() -> bool:
    try:
        database.stock_hot_rankings.collection.database.client.admin.command("ping")
        return True
    except Exception:
        return False


def read_collection(collection, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    try:
        records = collection.find_many(query or {})
        return [to_jsonable(record) for record in records]
    except Exception as exc:
        raise DatabaseUnavailable(str(exc)) from exc


def collection_count(collection) -> int | None:
    try:
        return collection.collection.count_documents({})
    except Exception:
        return None


def collection_preview(collection, limit: int = 5) -> list[dict[str, Any]]:
    try:
        records = collection.collection.find({}).sort("_id", -1).limit(limit)
        return [to_jsonable(record) for record in records]
    except Exception:
        return []


def package_available(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


def check_hithink_financial() -> dict[str, Any]:
    try:
        return hithink_financial.check_connection()
    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
        }


def build_data_source_status(check: bool = False) -> list[dict[str, Any]]:
    sources = []
    for metadata in list_sources():
        dependency_ready = not metadata.dependency or package_available(metadata.dependency)
        credential_ready = not metadata.credential_env or bool(
            iwencai_provider.get_setting(metadata.credential_env)
        )
        enabled = dependency_ready and credential_ready
        if metadata.local_service and dependency_ready:
            message = "SDK 已安装；运行时还需启动本地服务"
        elif not dependency_ready:
            message = f"未安装依赖 {metadata.dependency}"
        elif not credential_ready:
            message = f"未配置 {metadata.credential_env}"
        else:
            message = metadata.description
        sources.append(
            {
                "id": metadata.source_id,
                "name": metadata.name,
                "type": metadata.kind,
                "enabled": enabled,
                "packageAvailable": dependency_ready,
                "credential": (
                    "无需 Token"
                    if not metadata.credential_env
                    else ("已配置" if credential_ready else f"未配置 {metadata.credential_env}")
                ),
                "status": "ready" if enabled else "blocked",
                "message": message,
                "capabilities": list(metadata.capabilities),
                "docUrl": metadata.docs_url,
            }
        )

    if check:
        checks = {
            hithink_financial.SOURCE_ID: check_hithink_financial,
        }
        for source in sources:
            checker = checks.get(source["id"])
            if not checker:
                continue
            result = checker()
            source["status"] = "online" if result["ok"] else "offline"
            source["message"] = result["message"]
            source["checkedAt"] = datetime.now().isoformat(timespec="seconds")

    return sources


def build_database_status() -> dict[str, Any]:
    collections = [
        ("stock_hot_rankings", "热榜缓存", database.stock_hot_rankings),
        ("stock_pool", "股票池", database.stock_pool),
        ("stock_daily_data", "每日行情", database.stock_daily_data),
        ("stock_history_data", "历史行情缓存", database.stock_history_data),
        ("stock_filter_result", "策略筛选结果", database.stock_filter_result),
    ]
    available = mongo_available()

    return {
        "ok": available,
        "name": "python",
        "uri": "mongodb://localhost:27017/",
        "checkedAt": datetime.now().isoformat(timespec="seconds"),
        "collections": [
            {
                "id": collection_id,
                "title": title,
                "count": collection_count(collection) if available else None,
                "preview": collection_preview(collection) if available else [],
            }
            for collection_id, title, collection in collections
        ],
    }


def value_from(record: dict[str, Any], candidates: list[str]) -> Any:
    for column in candidates:
        value = record.get(column)
        if value not in (None, ""):
            return value
    return None


def split_name_code(value: Any) -> tuple[Any, Any]:
    if not isinstance(value, str):
        return value, None
    text = value.strip()
    if not text:
        return None, None
    parts = text.replace("/", " ").split()
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return text, None


def normalize_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for index, record in enumerate(records, start=1):
        raw_name_code = value_from(record, ["名称/代码"])
        parsed_name, parsed_code = split_name_code(raw_name_code)
        rank = value_from(record, ["当前排名", "排名", "rank"]) or index
        code = (
            value_from(record, ["股票代码", "代码", "证券代码", "ticker", "thscode"])
            or parsed_code
        )
        name = value_from(record, ["股票简称", "股票名称", "名称", "name"]) or parsed_name
        rows.append(
            {
                "rank": rank,
                "code": code,
                "name": name,
                "price": value_from(record, ["最新价", "价格", "last_price"]),
                "change": value_from(
                    record,
                    ["涨跌幅", "涨跌幅%", "涨跌额", "price_change_ratio_pct"],
                ),
                "heat": value_from(
                    record,
                    [
                        "关注",
                        "综合热度",
                        "排名较昨日变动",
                        "heat",
                        "rank_change",
                        "seal_money",
                    ],
                ),
                "raw": record,
            }
        )
    return rows


def build_display_columns(records: list[dict[str, Any]]) -> list[str]:
    preferred = [
        "当前排名",
        "排名",
        "排名较昨日变动",
        "股票代码",
        "代码",
        "证券代码",
        "股票简称",
        "股票名称",
        "名称/代码",
        "关注",
        "综合热度",
        "最新价",
        "涨跌额",
        "涨跌幅",
        "rank",
        "ticker",
        "name",
        "heat",
        "rank_change",
        "last_price",
        "price_change_ratio_pct",
        "continue_day_text",
        "limit_up_reason",
    ]
    seen = []
    available = set()
    for record in records[:10]:
        available.update(record.keys())
    for column in preferred:
        if column in available and column not in seen:
            seen.append(column)
    for column in sorted(available):
        if column not in seen:
            seen.append(column)
    return seen[:8]


def cache_ranking(payload: dict[str, Any]) -> None:
    if not mongo_available():
        return
    database.stock_hot_rankings.collection.replace_one(
        {"id": payload["id"]},
        payload,
        upsert=True,
    )


def read_cached_rankings() -> list[dict[str, Any]]:
    try:
        cached = read_collection(database.stock_hot_rankings)
    except DatabaseUnavailable:
        return []
    cache_by_id = {item["id"]: item for item in cached}
    return [cache_by_id[item["id"]] for item in HOT_RANKINGS if item["id"] in cache_by_id]


def empty_payload(config: dict[str, Any], error: str | None = None) -> dict[str, Any]:
    return {
        "id": config["id"],
        "title": config["title"],
        "source": config["source"],
        "provider": config.get("provider"),
        "description": config["description"],
        "function": config["function"],
        "params": resolve_params(config["params"]),
        "docUrl": config["docUrl"],
        "updatedAt": None,
        "rowCount": 0,
        "columns": [],
        "rows": [],
        "error": error,
    }


def fetch_hot_ranking(config: dict[str, Any], limit: int) -> dict[str, Any]:
    try:
        df, params = fetch_hot_ranking_frame(config)
        records = dataframe_records(df, limit=limit)
        payload = {
            "id": config["id"],
            "title": config["title"],
            "source": config["source"],
            "provider": config.get("provider"),
            "description": config["description"],
            "function": config["function"],
            "params": params,
            "docUrl": config["docUrl"],
            "updatedAt": datetime.now().isoformat(timespec="seconds"),
            "rowCount": len(records),
            "columns": build_display_columns(records),
            "rows": normalize_rows(records),
            "error": None,
        }
        cache_ranking(payload)
        return payload
    except Exception as exc:
        cached = read_cached_ranking(config["id"])
        if cached:
            cached["error"] = f"刷新失败，正在显示缓存: {exc}"
            return cached
        return empty_payload(config, error=str(exc))


def read_cached_ranking(ranking_id: str) -> dict[str, Any] | None:
    try:
        records = read_collection(database.stock_hot_rankings, {"id": ranking_id})
    except DatabaseUnavailable:
        return None
    return records[0] if records else None


def list_hot_rankings(refresh: bool, limit: int) -> list[dict[str, Any]]:
    if refresh:
        return [fetch_hot_ranking(config, limit=limit) for config in HOT_RANKINGS]

    cached = read_cached_rankings()
    cached_by_id = {item["id"]: item for item in cached}
    return [
        cached_by_id.get(config["id"]) or empty_payload(config)
        for config in HOT_RANKINGS
    ]


def get_hot_ranking(ranking_id: str, refresh: bool, limit: int) -> dict[str, Any]:
    config = RANKING_BY_ID.get(ranking_id)
    if not config:
        raise ValueError("未知榜单")
    if refresh:
        return fetch_hot_ranking(config, limit=limit)
    cached = read_cached_ranking(ranking_id)
    return cached or empty_payload(config)


def parse_strategy_source_ids(value: str | None) -> list[str] | None:
    if not value or value == "all":
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def build_strategy_payload(source_ids: list[str] | None, limit: int) -> dict[str, Any]:
    sources = load_strategy_sources(source_ids)
    stocks = [
        stock.to_dict()
        for source in sources
        for stock in source.stocks
    ]
    return {
        "sources": [source.to_dict(include_stocks=False) for source in sources],
        "items": stocks[:limit],
        "stockCount": len(stocks),
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
    }


class StockApiHandler(BaseHTTPRequestHandler):
    server_version = "StockDashboardApi/2.0"

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            path = parsed.path.rstrip("/") or "/"

            if path == "/api/health":
                self.send_json(
                    {
                        "ok": True,
                        "service": "stock-dashboard-api",
                        "dataSource": hithink_financial.SOURCE_NAME,
                        "time": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                return

            if path == "/api/summary":
                hot_count = collection_count(database.stock_hot_rankings)
                self.send_json(
                    {
                        "mongoAvailable": hot_count is not None,
                        "hotRankingCount": hot_count,
                        "configuredRankingCount": len(HOT_RANKINGS),
                        "dataSource": hithink_financial.SOURCE_NAME,
                    }
                )
                return

            if path == "/api/data-sources":
                check = parse_bool(params.get("check", [None])[0])
                self.send_json(
                    {
                        "items": build_data_source_status(check=check),
                        "checkedAt": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                return

            if path == "/api/database":
                self.send_json(build_database_status())
                return

            if path == "/api/iwencai/status":
                self.send_json(iwencai_provider.build_status())
                return

            if path == "/api/iwencai/latest":
                latest = iwencai_provider.load_latest()
                self.send_json({"item": latest})
                return

            if path == "/api/stocks/history":
                symbol = params.get("symbol", [""])[0]
                name = params.get("name", [""])[0]
                period = params.get("period", ["daily"])[0]
                adjust = params.get("adjust", ["none"])[0]
                start_date, end_date = resolve_history_dates(
                    params.get("startDate", [None])[0],
                    params.get("endDate", [None])[0],
                )
                self.send_json(
                    {
                        "item": fetch_stock_history(
                            symbol=symbol,
                            period=period,
                            start_date=start_date,
                            end_date=end_date,
                            adjust=adjust,
                            name=name,
                        )
                    }
                )
                return

            if path == "/api/strategy-sources":
                source_ids = parse_strategy_source_ids(params.get("source", [None])[0])
                sources = load_strategy_sources(source_ids)
                self.send_json(
                    {
                        "items": [source.to_dict(include_stocks=False) for source in sources],
                        "generatedAt": datetime.now().isoformat(timespec="seconds"),
                    }
                )
                return

            if path == "/api/strategy-stocks":
                source_ids = parse_strategy_source_ids(params.get("source", [None])[0])
                limit = parse_int(params.get("limit", [None])[0], default=300, minimum=1, maximum=2000)
                self.send_json(build_strategy_payload(source_ids, limit=limit))
                return

            if path == "/api/hot-rankings":
                refresh = parse_bool(params.get("refresh", [None])[0])
                limit = parse_int(params.get("limit", [None])[0], default=80, minimum=5, maximum=300)
                self.send_json(
                    {
                        "items": list_hot_rankings(refresh=refresh, limit=limit),
                        "mongoAvailable": mongo_available(),
                    }
                )
                return

            if path.startswith("/api/hot-rankings/"):
                ranking_id = path.rsplit("/", 1)[-1]
                refresh = parse_bool(params.get("refresh", [None])[0])
                limit = parse_int(params.get("limit", [None])[0], default=80, minimum=5, maximum=300)
                self.send_json(
                    {
                        "item": get_hot_ranking(ranking_id=ranking_id, refresh=refresh, limit=limit),
                        "mongoAvailable": mongo_available(),
                    }
                )
                return

            self.send_json({"error": "接口不存在"}, status=404)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": f"服务处理失败: {exc}"}, status=500)

    def do_POST(self) -> None:
        try:
            path = urlparse(self.path).path.rstrip("/") or "/"
            if path == "/api/stocks/history/prefetch":
                payload = self.read_json_body()
                stocks = payload.get("stocks")
                if not isinstance(stocks, list):
                    raise ValueError("stocks 必须是股票列表")
                if len(stocks) > 300:
                    raise ValueError("单次最多预缓存 300 只股票")
                symbols = []
                for item in stocks:
                    if isinstance(item, str):
                        symbols.append(item)
                    elif isinstance(item, dict):
                        symbol = item.get("symbol") or item.get("股票代码")
                        if symbol:
                            symbols.append(str(symbol))
                start_date, end_date = resolve_history_dates(
                    payload.get("startDate"),
                    payload.get("endDate"),
                )
                workers = parse_int(
                    str(payload.get("workers", 4)),
                    default=4,
                    minimum=1,
                    maximum=8,
                )
                result = hithink_financial.prefetch_stock_histories(
                    symbols,
                    start_date,
                    end_date,
                    adjust=str(payload.get("adjust") or "none"),
                    workers=workers,
                )
                self.send_json({"item": result})
                return

            if path != "/api/iwencai/query":
                self.send_json({"error": "接口不存在"}, status=404)
                return

            payload = self.read_json_body()
            query = payload.get("query")
            if not isinstance(query, str):
                raise ValueError("query 必须是字符串")
            page_size = parse_int(str(payload.get("pageSize", 50)), default=50, minimum=1, maximum=100)
            max_pages = parse_int(str(payload.get("maxPages", 100)), default=100, minimum=1, maximum=100)
            timeout = parse_int(str(payload.get("timeout", 60)), default=60, minimum=10, maximum=120)
            result = iwencai_provider.run_query(
                query,
                page_size=page_size,
                max_pages=max_pages,
                timeout=timeout,
            )
            self.send_json({"item": result})
        except (ValueError, iwencai_provider.IwencaiError) as exc:
            self.send_json({"error": str(exc)}, status=400)
        except Exception as exc:
            self.send_json({"error": f"请求处理失败: {exc}"}, status=500)

    def read_json_body(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length 无效") from exc
        if content_length <= 0:
            raise ValueError("请求内容不能为空")
        if content_length > 64 * 1024:
            raise ValueError("请求内容过大")
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("请求 JSON 格式无效") from exc
        if not isinstance(payload, dict):
            raise ValueError("请求 JSON 必须是对象")
        return payload

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(to_jsonable(payload), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[api] {self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the stock dashboard API server.")
    parser.add_argument("--host", default=os.getenv("API_HOST", "127.0.0.1"))
    parser.add_argument("--port", default=int(os.getenv("API_PORT", "8001")), type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), StockApiHandler)
    print(f"Stock dashboard API running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
