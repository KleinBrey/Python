from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from stock_app.data_sources.akshare_provider import HOT_RANKINGS, fetch_hot_ranking_frame, resolve_params  # noqa: E402
from stock_app.database import collections as database  # noqa: E402

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
        code = value_from(record, ["股票代码", "代码", "证券代码"]) or parsed_code
        name = value_from(record, ["股票简称", "股票名称", "名称"]) or parsed_name
        rows.append(
            {
                "rank": rank,
                "code": code,
                "name": name,
                "price": value_from(record, ["最新价", "价格"]),
                "change": value_from(record, ["涨跌幅", "涨跌幅%", "涨跌额"]),
                "heat": value_from(record, ["关注", "综合热度", "排名较昨日变动"]),
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
                        "dataSource": "akshare",
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
                        "dataSource": "akshare",
                    }
                )
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
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
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
