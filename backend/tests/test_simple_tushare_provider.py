from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from backend.simple.provider.tushare_provider import (
    TushareProvider,
    create_tushare_client,
)


SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _timestamp_ms(value: str) -> int:
    timestamp = datetime.strptime(value, "%Y%m%d")
    timestamp = timestamp.replace(tzinfo=SHANGHAI_TIMEZONE)
    return int(timestamp.timestamp() * 1000)


class FakeProApi:
    def stock_basic(self, **kwargs):
        return pd.DataFrame()


def test_requires_token_without_injected_api(monkeypatch):
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider._TushareSettings",
        lambda: type(
            "Settings",
            (),
            {
                "token": "",
                "use_relay": True,
                "relay_url": "https://t.xiaodefa.top",
            },
        )(),
    )

    with pytest.raises(ValueError, match="TUSHARE_TOKEN"):
        TushareProvider()


def test_uses_token_from_environment(monkeypatch):
    received = {}
    client = FakeProApi()
    monkeypatch.setenv("TUSHARE_TOKEN", "test-token")

    def fake_pro_api(token, timeout):
        received["token"] = token
        received["timeout"] = timeout
        return client

    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider.ts.pro_api", fake_pro_api
    )

    provider = TushareProvider()

    assert received == {"token": "test-token", "timeout": 30}
    assert provider.pro_api is client
    assert provider.pro_api._DataApi__http_url == "https://t.xiaodefa.top"


def test_allows_overriding_http_url(monkeypatch):
    received = {}
    client = FakeProApi()

    def fake_pro_api(token, timeout):
        received["token"] = token
        received["timeout"] = timeout
        return client

    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider.ts.pro_api", fake_pro_api
    )

    create_tushare_client(
        "test-token", http_url="https://example.test/tushare"
    )

    assert received == {"token": "test-token", "timeout": 30}
    assert client._DataApi__http_url == "https://example.test/tushare"


def test_can_disable_relay_and_use_official_endpoint(monkeypatch):
    client = FakeProApi()
    client._DataApi__http_url = "http://api.waditu.com/dataapi"

    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider.ts.pro_api",
        lambda token, timeout: client,
    )

    provider = TushareProvider("official-token", use_relay=False)

    assert provider.pro_api is client
    assert client._DataApi__http_url == "http://api.waditu.com/dataapi"


def test_fetch_stock_list_adapts_tushare_columns():
    received = {}

    class StockListApi(FakeProApi):
        def stock_basic(self, **kwargs):
            received.update(kwargs)
            return pd.DataFrame(
                [
                    {
                        "ts_code": "601899.SH",
                        "symbol": "601899",
                        "name": "紫金矿业",
                        "exchange": "SSE",
                    },
                    {
                        "ts_code": "000001.SZ",
                        "symbol": "000001",
                        "name": "平安银行",
                        "exchange": "SZSE",
                    },
                    {
                        "ts_code": "920001.BJ",
                        "symbol": "920001",
                        "name": "北交所示例",
                        "exchange": "BSE",
                    },
                ]
            )

    items = TushareProvider(pro_api=StockListApi()).fetch_stock_list()["data"]["item"]

    assert received == {
        "exchange": "",
        "list_status": "L",
        "fields": "ts_code,symbol,name,exchange",
    }
    assert items == [
        {
            "ticker": "601899",
            "name": "紫金矿业",
            "exchange": "SH",
            "source": "Tushare",
        },
        {
            "ticker": "000001",
            "name": "平安银行",
            "exchange": "SZ",
            "source": "Tushare",
        },
        {
            "ticker": "920001",
            "name": "北交所示例",
            "exchange": "BJ",
            "source": "Tushare",
        },
    ]


def test_fetch_historical_adapts_fields_units_and_order(monkeypatch):
    received = {}
    frame = pd.DataFrame(
        [
            {
                "ts_code": "601899.SH",
                "trade_date": "20260818",
                "open": 25.5,
                "high": 26.0,
                "low": 25.2,
                "close": 25.8,
                "vol": 20_000,
                "amount": 51_500,
            },
            {
                "ts_code": "601899.SH",
                "trade_date": "20260817",
                "open": 25.1,
                "high": 25.8,
                "low": 24.9,
                "close": 25.5,
                "vol": 10_000,
                "amount": 25_300,
            },
        ]
    )

    def fake_pro_bar(**kwargs):
        received.update(kwargs)
        return frame

    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider.ts.pro_bar", fake_pro_bar
    )
    api = FakeProApi()

    result = TushareProvider(pro_api=api).fetch_historical(
        "601899.SH",
        _timestamp_ms("20260801"),
        _timestamp_ms("20260818"),
    )
    items = result["data"]["item"]

    assert received == {
        "ts_code": "601899.SH",
        "api": api,
        "start_date": "20260801",
        "end_date": "20260818",
        "asset": "E",
        "freq": "D",
        "adj": "qfq",
    }
    assert [item["close_price"] for item in items] == [25.5, 25.8]
    assert items[0]["volume"] == 1_000_000
    assert items[0]["turnover"] == 25_300_000
    assert items[0]["source"] == "Tushare"

    trade_date = pd.to_datetime(items[0]["date_ms"], unit="ms", utc=True)
    assert trade_date.tz_convert("Asia/Shanghai").strftime("%Y-%m-%d") == "2026-08-17"


@pytest.mark.parametrize(
    ("interval", "adjust", "expected_frequency", "expected_adjustment"),
    [
        ("daily", "raw", "D", None),
        ("weekly", "backward", "W", "hfq"),
        ("monthly", "forward", "M", "qfq"),
    ],
)
def test_fetch_historical_maps_interval_and_adjustment(
    monkeypatch,
    interval,
    adjust,
    expected_frequency,
    expected_adjustment,
):
    received = {}

    def fake_pro_bar(**kwargs):
        received.update(kwargs)
        return pd.DataFrame()

    monkeypatch.setattr(
        "backend.simple.provider.tushare_provider.ts.pro_bar", fake_pro_bar
    )

    TushareProvider(pro_api=FakeProApi()).fetch_historical(
        "000001",
        _timestamp_ms("20260801"),
        _timestamp_ms("20260818"),
        interval=interval,
        adjust=adjust,
    )

    assert received["freq"] == expected_frequency
    assert received["adj"] == expected_adjustment
