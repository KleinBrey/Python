from dataclasses import dataclass

import pandas as pd
import pytest

from backend.app.provider import tushare_provider as module
from backend.app.provider.tushare_provider import (
    TushareProvider,
    create_tushare_client,
)


class FakeProApi:
    pass


@dataclass
class SettingsStub:
    private_token: str
    relay_token: str
    use_relay: bool
    relay_url: str


def _settings(**overrides):
    values = {
        "private_token": "private-token",
        "relay_token": "relay-token",
        "use_relay": True,
        "relay_url": "https://relay.example.test",
    }
    values.update(overrides)
    return SettingsStub(**values)


def test_create_client_uses_relay_settings(monkeypatch):
    received = {}
    client = FakeProApi()

    def fake_pro_api(token, timeout):
        received.update(token=token, timeout=timeout)
        return client

    monkeypatch.setattr(module, "TushareSettings", lambda: _settings())
    monkeypatch.setattr(module.ts, "pro_api", fake_pro_api)

    assert create_tushare_client(timeout=15) is client
    assert received == {"token": "relay-token", "timeout": 15}
    assert client._DataApi__http_url == "https://relay.example.test"


def test_create_client_can_use_official_endpoint(monkeypatch):
    received = {}
    client = FakeProApi()

    def fake_pro_api(token, timeout):
        received.update(token=token, timeout=timeout)
        return client

    monkeypatch.setattr(
        module,
        "TushareSettings",
        lambda: _settings(use_relay=False),
    )
    monkeypatch.setattr(module.ts, "pro_api", fake_pro_api)

    assert create_tushare_client() is client
    assert received == {"token": "private-token", "timeout": 30}
    assert not hasattr(client, "_DataApi__http_url")


def test_provider_uses_created_client(monkeypatch):
    client = FakeProApi()
    monkeypatch.setattr(module, "create_tushare_client", lambda timeout=30: client)

    provider = TushareProvider(timeout=10)

    assert provider.pro is client


def test_fetch_stock_list_returns_tushare_frame(monkeypatch):
    received = {}
    expected = pd.DataFrame(
        [["601899", "紫金矿业", "SSE", "主板"]],
        columns=["symbol", "name", "exchange", "market"],
    )

    class StockApi(FakeProApi):
        def stock_basic(self, **kwargs):
            received.update(kwargs)
            return expected

    monkeypatch.setattr(module, "create_tushare_client", lambda timeout=30: StockApi())

    result = TushareProvider().fetch_stock_list()

    pd.testing.assert_frame_equal(result, expected)
    assert received == {
        "exchange": "",
        "list_status": "L",
        "fields": "symbol,name,exchange,market",
    }


def test_fetch_historical_calls_daily(monkeypatch):
    received = {}
    expected = pd.DataFrame(
        [["601899.SH", "20260818", 25.5, 26.0, 25.2, 25.8, 20_000, 51_500]],
        columns=[
            "ts_code",
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "vol",
            "amount",
        ],
    )

    class DailyApi(FakeProApi):
        def daily(self, **kwargs):
            received.update(kwargs)
            return expected

    monkeypatch.setattr(module, "create_tushare_client", lambda timeout=30: DailyApi())

    result = TushareProvider().fetch_historical(
        "601899.SH",
        1_754_006_400_000,
        1_755_475_200_000,
    )

    pd.testing.assert_frame_equal(result, expected)
    assert received == {
        "ts_code": "601899.SH",
        "start_date": "20250801",
        "end_date": "20250818",
    }


def test_fetch_daily_basic_normalizes_market_cap(monkeypatch):
    class BasicApi(FakeProApi):
        def daily_basic(self, **kwargs):
            return pd.DataFrame(
                [
                    ["601899.SH", "20260818", 123.5],
                    ["000001.SZ", "20260818", None],
                ],
                columns=["ts_code", "trade_date", "total_mv"],
            )

    monkeypatch.setattr(module, "create_tushare_client", lambda timeout=30: BasicApi())

    result = TushareProvider().fetch_daily_basic("20260818")

    assert result.to_dict(orient="records") == [
        {"symbol": "601899", "market_cap": 1_235_000.0}
    ]


@pytest.mark.parametrize(
    ("interval", "adjust", "expected_frequency", "expected_adjustment"),
    [
        ("daily", "raw", "D", None),
        ("weekly", "backward", "W", "hfq"),
        ("monthly", "forward", "M", "qfq"),
    ],
)
def test_fetch_pro_bar_maps_interval_and_adjustment(
    monkeypatch,
    interval,
    adjust,
    expected_frequency,
    expected_adjustment,
):
    received = {}
    client = FakeProApi()
    monkeypatch.setattr(module, "create_tushare_client", lambda timeout=30: client)

    def fake_pro_bar(**kwargs):
        received.update(kwargs)
        return pd.DataFrame()

    monkeypatch.setattr(module.ts, "pro_bar", fake_pro_bar)

    result = TushareProvider().fetch_pro_bar(
        "000001",
        1_754_006_400_000,
        1_755_475_200_000,
        interval=interval,
        adjust=adjust,
    )

    assert result.empty
    assert received["api"] is client
    assert received["ts_code"] == "000001.SZ"
    assert received["freq"] == expected_frequency
    assert received["adj"] == expected_adjustment
