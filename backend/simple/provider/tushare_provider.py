"""使用 Tushare Pro 获取 A 股基础信息和历史行情。

默认通过中转地址请求；将 ``use_relay`` 设为 ``false`` 即可切换到
Tushare 官方地址。Token 只从构造参数或 ``backend/.env`` / 环境变量读取，
不会硬编码在源码中。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
from pydantic_settings import BaseSettings, SettingsConfigDict
import tushare as ts

from backend.simple.utils.symbol import exchange_for, validate_symbol

DEFAULT_RELAY_URL = "https://t.xiaodefa.top"

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class TushareSettings(BaseSettings):
    """从环境变量和 backend/.env 读取 Tushare 配置。"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="TUSHARE_",
        extra="ignore",
    )

    private_token: str = ""
    relay_token: str = ""
    use_relay: bool = True
    relay_url: str = DEFAULT_RELAY_URL


def create_tushare_client(
    timeout: int = 30,
) -> None:

    settings = TushareSettings()
    private_token = settings.private_token
    relay_token = settings.relay_token
    relay_enabled = settings.use_relay

    # 没有设置中转直接返回官方client
    if relay_enabled:
        client = ts.pro_api(relay_token, timeout=timeout)
        client._DataApi__http_url = settings.relay_url
        return client
    else:
        client = ts.pro_api(private_token, timeout=timeout)
        return client


class TushareProvider:
    """把 Tushare Pro 返回的数据适配为 simple 服务使用的结构。"""

    source = "Tushare"

    _INTERVAL_MAP = {
        "1d": "D",
        "daily": "D",
        "1w": "W",
        "weekly": "W",
        "1mo": "M",
        "monthly": "M",
    }
    _ADJUST_MAP = {
        "": None,
        "none": None,
        "raw": None,
        "forward": "qfq",
        "qfq": "qfq",
        "backward": "hfq",
        "hfq": "hfq",
    }
    _EXCHANGE_MAP = {
        "SSE": "SH",
        "SZSE": "SZ",
        "BSE": "BJ",
    }

    def __init__(
        self,
        timeout: int = 30,
    ) -> None:

        self.pro_api = create_tushare_client(
            timeout=timeout,
        )

    @staticmethod
    def _timestamp_to_date(timestamp_ms: int) -> str:
        """把毫秒时间戳转换为上海时区的 YYYYMMDD 日期。"""

        timestamp = pd.to_datetime(timestamp_ms, unit="ms", utc=True)
        return timestamp.tz_convert("Asia/Shanghai").strftime("%Y%m%d")

    @staticmethod
    def _ts_code(value: str) -> str:
        """把 simple 支持的股票代码统一转换为 Tushare TS 代码。"""

        code = validate_symbol(value)
        return f"{code}.{exchange_for(code)}"

    def fetch_stock_list(self) -> dict:
        """获取沪、深、北交易所当前正常上市的全部 A 股。"""

        frame = self.pro_api.stock_basic(
            exchange="",
            list_status="L",
            fields="ts_code,symbol,name,exchange",
        )
        if frame is None or frame.empty:
            return {"data": {"item": []}}

        required_columns = {"symbol", "name", "exchange"}
        missing_columns = required_columns.difference(frame.columns)
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Tushare 股票列表缺少字段: {missing_text}")

        items = []
        for row in frame.itertuples(index=False):
            code = validate_symbol(row.symbol)
            exchange = self._EXCHANGE_MAP.get(str(row.exchange).upper())
            if exchange is None:
                exchange = exchange_for(code)
            items.append(
                {
                    "ticker": code,
                    "name": row.name,
                    "exchange": exchange,
                    "source": self.source,
                }
            )

        return {"data": {"item": items}}

    def fetch_historical(
        self,
        thscode: str,
        start: int,
        end: int,
        interval: str = "1d",
        adjust: str = "forward",
        offset: int = 0,
    ) -> dict:
        """获取历史行情，并返回现有 Service 能处理的字段和单位。"""

        try:
            frequency = self._INTERVAL_MAP[interval.lower()]
        except KeyError as error:
            raise ValueError(f"Tushare 不支持行情周期: {interval!r}") from error

        try:
            adjustment = self._ADJUST_MAP[adjust.lower()]
        except KeyError as error:
            raise ValueError(f"Tushare 不支持复权方式: {adjust!r}") from error

        if offset < 0:
            raise ValueError("offset 不能小于 0")

        frame = ts.pro_bar(
            api=self.pro_api,
            ts_code=self._ts_code(thscode),
            start_date=self._timestamp_to_date(start),
            end_date=self._timestamp_to_date(end),
            asset="E",
            freq=frequency,
            adj=adjustment,
        )
        if frame is None or frame.empty:
            return {"data": {"item": []}}

        column_map = {
            "trade_date": "date",
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "vol": "volume",
            "amount": "turnover",
        }
        missing_columns = set(column_map).difference(frame.columns)
        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Tushare 行情数据缺少字段: {missing_text}")

        result = frame[list(column_map)].rename(columns=column_map).copy()
        result["date"] = pd.to_datetime(result["date"], format="%Y%m%d", errors="raise")
        result = result.sort_values("date").iloc[offset:].reset_index(drop=True)

        shanghai_dates = result.pop("date").dt.tz_localize("Asia/Shanghai")
        result["date_ms"] = shanghai_dates.astype("int64") // 1_000_000

        price_columns = ["open_price", "high_price", "low_price", "close_price"]
        for column in price_columns:
            result[column] = pd.to_numeric(result[column], errors="raise")

        # daily/pro_bar 的成交量单位为手、成交额单位为千元；统一换算成股和元。
        result["volume"] = pd.to_numeric(result["volume"], errors="raise") * 100
        result["turnover"] = pd.to_numeric(result["turnover"], errors="raise") * 1_000
        result["source"] = self.source

        return {"data": {"item": result.to_dict(orient="records")}}
