"""同花顺问财自然语言选股 OpenAPI 适配器。"""

from __future__ import annotations

import csv
import json
import os
import re
import secrets
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from data.paths import source_data_dir
from data.settings import get_setting

DEFAULT_BASE_URL = "https://openapi.iwencai.com"
SKILL_ID = "hithink-astock-selector"
SKILL_VERSION = "1.0.0"


class IwencaiError(RuntimeError):
    pass


def normalize_query(query: str) -> tuple[str, list[str]]:
    """清理明显误输入，并改写成问财更稳定识别的金融表述。"""

    normalized = " ".join(query.split())
    notes: list[str] = []

    without_noise = re.sub(r"([\u4e00-\u9fffA-Za-z])\1{3,}", "", normalized)
    if without_noise != normalized:
        normalized = " ".join(without_noise.split())
        normalized = re.sub(
            r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])",
            "",
            normalized,
        )
        notes.append("已清除连续重复的误输入字符")

    rewrites = (
        (
            re.compile(
                r"最近5个交易日均成交量\s*/\s*"
                r"最近5个交易日前20个交易日均成交量大于等于\s*1\.5(?:倍)?"
            ),
            "最近5个交易日平均成交量大于此前20个交易日平均成交量的1.5倍",
            "已将成交量比值改写为标准倍数条件",
        ),
        (
            re.compile(r"最近5日涨幅"),
            "最近5个交易日涨幅",
            "已明确涨幅按最近5个交易日计算",
        ),
        (
            re.compile(r"按(?:现在|当前)个股热度排序"),
            "按最近一个交易日个股热度从高到低排序",
            "已将当前热度改为最近一个交易日热度",
        ),
    )
    for pattern, replacement, note in rewrites:
        rewritten = pattern.sub(replacement, normalized)
        if rewritten != normalized:
            normalized = rewritten
            notes.append(note)

    return normalized, notes


def resolve_project_dir() -> Path:
    configured = os.getenv("IWENCAI_PROJECT_DIR", "").strip()
    return Path(configured).expanduser() if configured else source_data_dir("iwencai")


def resolve_output_dir() -> Path:
    configured = os.getenv("IWENCAI_OUTPUT_DIR", "").strip()
    return Path(configured).expanduser() if configured else resolve_project_dir() / "results"


def build_ssl_context() -> ssl.SSLContext:
    candidates = [
        os.environ.get("SSL_CERT_FILE", ""),
        "/etc/ssl/cert.pem",
        "/opt/homebrew/etc/openssl@3/cert.pem",
        "/opt/homebrew/etc/ca-certificates/cert.pem",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


def request_page(
    *,
    base_url: str,
    api_key: str,
    query: str,
    page: int,
    page_size: int,
    timeout: int,
    context: ssl.SSLContext,
) -> dict[str, Any]:
    payload = {
        "query": query,
        "page": str(page),
        "limit": str(page_size),
        "is_cache": "1",
        "expand_index": "true",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Claw-Call-Type": "normal",
        "X-Claw-Skill-Id": SKILL_ID,
        "X-Claw-Skill-Version": SKILL_VERSION,
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": secrets.token_hex(32),
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/query2data",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            raise IwencaiError("IWENCAI_API_KEY 无效或已过期") from exc
        raise IwencaiError(f"问财接口返回 HTTP {exc.code}：{detail[:300]}") from exc
    except urllib.error.URLError as exc:
        raise IwencaiError(f"问财网络连接失败：{exc.reason}") from exc

    try:
        result = json.loads(body)
    except json.JSONDecodeError as exc:
        raise IwencaiError(f"问财返回了无法解析的内容：{body[:300]}") from exc
    if not isinstance(result, dict):
        raise IwencaiError("问财返回格式异常")
    return result


def fetch_all(
    *,
    query: str,
    page_size: int = 50,
    max_pages: int = 100,
    timeout: int = 60,
) -> tuple[list[dict[str, Any]], dict[str, Any], int]:
    api_key = get_setting("IWENCAI_API_KEY")
    if not api_key:
        raise IwencaiError("未配置 IWENCAI_API_KEY")
    if "*" in api_key or "\\" in api_key:
        raise IwencaiError("IWENCAI_API_KEY 看起来仍是脱敏值")

    base_url = get_setting("IWENCAI_BASE_URL", DEFAULT_BASE_URL)
    context = build_ssl_context()
    rows: list[dict[str, Any]] = []
    first_response: dict[str, Any] = {}
    expected_total: int | None = None
    pages_fetched = 0

    for page in range(1, max_pages + 1):
        response = request_page(
            base_url=base_url,
            api_key=api_key,
            query=query,
            page=page,
            page_size=page_size,
            timeout=timeout,
            context=context,
        )
        if page == 1:
            first_response = response
            try:
                expected_total = int(response.get("code_count", 0))
            except (TypeError, ValueError):
                expected_total = None

        page_rows = response.get("datas") or []
        if not isinstance(page_rows, list):
            raise IwencaiError(f"第 {page} 页 datas 字段不是列表")
        rows.extend(item for item in page_rows if isinstance(item, dict))
        pages_fetched = page

        if not page_rows:
            break
        if expected_total is not None and len(rows) >= expected_total:
            break
        if len(page_rows) < page_size:
            break
    else:
        if expected_total is None or len(rows) < expected_total:
            raise IwencaiError(f"达到最大分页数 {max_pages}，结果尚未获取完整")

    return rows, first_response, pages_fetched


def csv_columns(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns


def write_outputs(payload: dict[str, Any]) -> dict[str, str]:
    output_dir = resolve_output_dir().resolve()
    history_dir = output_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    paths = {
        "latestJson": output_dir / "latest.json",
        "latestCsv": output_dir / "latest.csv",
        "historyJson": history_dir / f"iwencai_{timestamp}.json",
        "historyCsv": history_dir / f"iwencai_{timestamp}.csv",
    }

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    for key in ("latestJson", "historyJson"):
        paths[key].write_text(json_text, encoding="utf-8")

    columns = csv_columns(payload["datas"])
    for key in ("latestCsv", "historyCsv"):
        with paths[key].open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            if columns:
                writer.writeheader()
                writer.writerows(payload["datas"])

    return {key: str(path) for key, path in paths.items()}


def run_query(
    query: str,
    *,
    page_size: int = 50,
    max_pages: int = 100,
    timeout: int = 60,
) -> dict[str, Any]:
    original_query = " ".join(query.split())
    normalized_query, normalization_notes = normalize_query(query)
    if not normalized_query:
        raise IwencaiError("查询条件不能为空")
    if len(normalized_query) > 2000:
        raise IwencaiError("查询条件过长，请控制在 2000 字以内")

    rows, first_response, pages_fetched = fetch_all(
        query=normalized_query,
        page_size=page_size,
        max_pages=max_pages,
        timeout=timeout,
    )
    payload = {
        "query": normalized_query,
        "original_query": original_query,
        "query_rewritten": normalized_query != original_query,
        "normalization_notes": normalization_notes,
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": "同花顺问财",
        "code_count": first_response.get("code_count", len(rows)),
        "rows_fetched": len(rows),
        "pages_fetched": pages_fetched,
        "chunks_info": first_response.get("chunks_info"),
        "columns": first_response.get("columns"),
        "datas": rows,
    }
    output_paths = write_outputs(payload)

    query_file = resolve_project_dir() / "query.txt"
    query_file.parent.mkdir(parents=True, exist_ok=True)
    query_file.write_text(f"{normalized_query}\n", encoding="utf-8")
    payload["output_paths"] = output_paths
    return payload


def load_latest() -> dict[str, Any] | None:
    latest_file = resolve_output_dir() / "latest.json"
    if not latest_file.is_file():
        return None
    try:
        payload = json.loads(latest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IwencaiError(f"无法读取最新问财结果：{exc}") from exc
    if not isinstance(payload, dict):
        raise IwencaiError("最新问财结果格式异常")
    return payload


def build_status() -> dict[str, Any]:
    latest = load_latest()
    return {
        "configured": bool(get_setting("IWENCAI_API_KEY")),
        "baseUrl": get_setting("IWENCAI_BASE_URL", DEFAULT_BASE_URL),
        "projectDir": str(resolve_project_dir()),
        "outputDir": str(resolve_output_dir()),
        "latest": latest,
    }
