"""同花顺 Financial API Python client 的本项目适配器。

接口、重试错误码和分页语义来自官方仓库：
https://github.com/HiThink-Tech/Financial-API/tree/main/python
"""

from __future__ import annotations

from datetime import datetime
from threading import local
import time
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from backend.app.providers.base import MarketDataProvider


_SHANGHAI = ZoneInfo("Asia/Shanghai")
_RETRY_CODES = {4001, 5001, 5002, 5003}


class HiThinkApiError(RuntimeError):
    def __init__(self, code: int, message: str, request_id: str | None = None):
        super().__init__(f"[hithink code={code}] {message} (request_id={request_id})")
        self.code = code
        self.message = message
        self.request_id = request_id


class HiThinkMarketDataProvider(MarketDataProvider):
    source_id = "hithink-finance"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://fuyao.aicubes.cn",
        *,
        timeout: int = 30,
        request_interval: float = 0.0,
    ):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = max(1, timeout)
        self.request_interval = max(0.0, request_interval)
        self._thread_state = local()

    def is_configured(self) -> bool:
        return bool(self.api_key and "*" not in self.api_key and "\\" not in self.api_key)

    def list_stocks(self) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        offset = 0
        limit = 10_000
        while True:
            data = self._get(
                "/api/meta/tickers/list",
                {
                    "exchange": "SH,SZ,BJ",
                    "asset_type": "a-share",
                    "limit": limit,
                    "offset": offset,
                },
            )
            page = data.get("item", [])
            rows.extend(page)
            if len(page) < limit:
                break
            offset += limit

        frame = pd.DataFrame(rows)
        columns = ["symbol", "code", "exchange", "name", "asset_type", "source"]
        if frame.empty:
            return pd.DataFrame(columns=columns)
        if "thscode" not in frame:
            raise ValueError("同花顺证券目录响应缺少 thscode")
        if "name" not in frame:
            frame["name"] = None
        frame["symbol"] = frame["thscode"].astype("string").str.upper()
        parsed = frame["symbol"].str.extract(r"^(?P<code>\d{6})\.(?P<exchange>SH|SZ|BJ)$")
        frame["code"] = parsed["code"]
        frame["exchange"] = parsed["exchange"]
        if "asset_type" not in frame:
            frame["asset_type"] = "a-share"
        frame["source"] = self.source_id
        return (
            frame[columns]
            .dropna(subset=["symbol", "code", "exchange"])
            .drop_duplicates("symbol", keep="last")
            .sort_values("symbol")
            .reset_index(drop=True)
        )

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        normalized = symbol.strip().upper()
        if not normalized or "." not in normalized:
            raise ValueError(f"thscode 必须包含交易所后缀: {symbol!r}")
        start = datetime.strptime(start_date, "%Y%m%d").replace(tzinfo=_SHANGHAI)
        end = datetime.strptime(end_date, "%Y%m%d").replace(
            hour=23, minute=59, second=59, microsecond=999000, tzinfo=_SHANGHAI
        )
        data = self._get(
            "/api/a-share/prices/historical",
            {
                "thscode": normalized,
                "interval": "1d",
                "start": int(start.timestamp() * 1000),
                "end": int(end.timestamp() * 1000),
                "adjust": "none",
            },
        )
        frame = pd.DataFrame(data.get("item", []))
        if frame.empty:
            return pd.DataFrame()
        frame = frame.rename(
            columns={
                "open_price": "open",
                "high_price": "high",
                "low_price": "low",
                "close_price": "close",
                "turnover": "amount",
            }
        )
        required = {"date_ms", "open", "high", "low", "close", "volume"}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"同花顺日 K 响应缺少字段: {', '.join(sorted(missing))}")
        frame["symbol"] = normalized
        frame["trade_date"] = (
            pd.to_datetime(frame["date_ms"], unit="ms", utc=True)
            .dt.tz_convert(_SHANGHAI)
            .dt.tz_localize(None)
            .dt.normalize()
        )
        for column in ("open", "high", "low", "close", "volume", "amount"):
            if column not in frame:
                frame[column] = pd.NA
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = frame.sort_values("trade_date")
        frame["pre_close"] = frame["close"].shift(1)
        frame["change"] = frame["close"] - frame["pre_close"]
        frame["pct_change"] = frame["change"] / frame["pre_close"] * 100
        frame["adjustment"] = "none"
        frame["source"] = self.source_id
        frame["ingested_at"] = datetime.now(_SHANGHAI).replace(tzinfo=None)
        return frame[
            [
                "symbol", "trade_date", "open", "high", "low", "close",
                "pre_close", "change", "pct_change", "volume", "amount",
                "adjustment", "source", "ingested_at",
            ]
        ]

    def _session(self) -> requests.Session:
        session = getattr(self._thread_state, "session", None)
        if session is None:
            session = requests.Session()
            self._thread_state.session = session
        return session

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("缺少 HITHINK_FINANCE_API_KEY")
        if self.request_interval:
            time.sleep(self.request_interval)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self._session().get(
                    f"{self.base_url}{path}",
                    params={key: value for key, value in params.items() if value is not None},
                    headers={"X-api-key": self.api_key},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                time.sleep(2**attempt)
                continue
            code = payload.get("code", -1)
            if code == 0:
                return payload.get("data") or {}
            if code in _RETRY_CODES and attempt < 2:
                time.sleep(2**attempt)
                continue
            raise HiThinkApiError(code, payload.get("message", ""), payload.get("request_id"))
        if last_error:
            raise last_error
        raise RuntimeError("同花顺 Financial API 请求失败")
