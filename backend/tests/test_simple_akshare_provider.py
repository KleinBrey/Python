import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from backend.simple.provider.akshare_provider import AkShareProvider


SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _timestamp_ms(value: str) -> int:
    timestamp = datetime.strptime(value, "%Y%m%d")
    timestamp = timestamp.replace(tzinfo=SHANGHAI_TIMEZONE)
    return int(timestamp.timestamp() * 1000)


def test_provider_bypasses_eastmoney_proxy(monkeypatch):
    monkeypatch.setenv("NO_PROXY", "localhost")
    monkeypatch.setenv("no_proxy", "localhost")

    AkShareProvider()

    assert ".eastmoney.com" in os.environ["NO_PROXY"].split(",")
    assert ".eastmoney.com" in os.environ["no_proxy"].split(",")


def test_fetch_stock_list_adds_exchange_and_source(monkeypatch):
    frame = pd.DataFrame(
        [
            {"code": "601899", "name": "紫金矿业"},
            {"code": "000001", "name": "平安银行"},
            {"code": "920001", "name": "北交所示例"},
        ]
    )
    monkeypatch.setattr(
        "backend.simple.provider.akshare_provider.ak.stock_info_a_code_name",
        lambda: frame,
    )

    items = AkShareProvider().fetch_stock_list()["data"]["item"]

    assert items == [
        {
            "ticker": "601899",
            "name": "紫金矿业",
            "exchange": "SH",
            "source": "AkShare",
        },
        {
            "ticker": "000001",
            "name": "平安银行",
            "exchange": "SZ",
            "source": "AkShare",
        },
        {
            "ticker": "920001",
            "name": "北交所示例",
            "exchange": "BJ",
            "source": "AkShare",
        },
    ]


def test_fetch_historical_adapts_akshare_columns(monkeypatch):
    received = {}

    def fake_stock_zh_a_hist(**kwargs):
        received.update(kwargs)
        return pd.DataFrame(
            [
                {
                    "日期": "2026-08-17",
                    "股票代码": "601899",
                    "开盘": 25.1,
                    "收盘": 25.5,
                    "最高": 25.8,
                    "最低": 24.9,
                    "成交量": 1_000_000,
                    "成交额": 25_300_000,
                }
            ]
        )

    monkeypatch.setattr(
        "backend.simple.provider.akshare_provider.ak.stock_zh_a_hist",
        fake_stock_zh_a_hist,
    )

    result = AkShareProvider(timeout=10).fetch_historical(
        "601899.SH",
        _timestamp_ms("20260801"),
        _timestamp_ms("20260818"),
    )
    item = result["data"]["item"][0]

    assert received == {
        "symbol": "601899",
        "period": "daily",
        "start_date": "20260801",
        "end_date": "20260818",
        "adjust": "qfq",
        "timeout": 10,
    }
    assert item["open_price"] == 25.1
    assert item["high_price"] == 25.8
    assert item["low_price"] == 24.9
    assert item["close_price"] == 25.5
    assert item["volume"] == 1_000_000
    assert item["turnover"] == 25_300_000
    assert item["source"] == "AkShare"

    trade_date = pd.to_datetime(item["date_ms"], unit="ms", utc=True)
    assert trade_date.tz_convert("Asia/Shanghai").strftime("%Y-%m-%d") == "2026-08-17"


def test_fetch_historical_falls_back_to_tencent(monkeypatch):
    def unavailable_eastmoney(**kwargs):
        raise requests.exceptions.ProxyError("proxy unavailable")

    received = {}

    def fake_tencent(**kwargs):
        received.update(kwargs)
        return pd.DataFrame(
            [
                {
                    "date": "2026-08-17",
                    "open": 25.1,
                    "close": 25.5,
                    "high": 25.8,
                    "low": 24.9,
                    "volume": 1_000_000,
                    "turnover": 0.01,
                    "amount": 25_300_000,
                }
            ]
        )

    monkeypatch.setattr(
        "backend.simple.provider.akshare_provider.ak.stock_zh_a_hist",
        unavailable_eastmoney,
    )
    monkeypatch.setattr(
        "backend.simple.provider.akshare_provider.ak.stock_zh_a_hist_tx",
        fake_tencent,
    )

    result = AkShareProvider(timeout=10).fetch_historical(
        "601899.SH",
        _timestamp_ms("20260801"),
        _timestamp_ms("20260818"),
    )

    assert received == {
        "symbol": "sh601899",
        "start_date": "20260801",
        "end_date": "20260818",
        "adjust": "qfq",
        "timeout": 10,
    }
    assert result["data"]["item"][0]["turnover"] == 25_300_000
