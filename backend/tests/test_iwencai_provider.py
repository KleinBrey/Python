import pandas as pd
import pytest

from backend.app.provider.iwencai_provider import IwencaiProvider


@pytest.mark.parametrize(
    ("method_name", "expected_query"),
    [
        ("fetch_hk_hot_rank", "港股关注度排名前50"),
        ("fetch_us_hot_rank", "美股关注度排名前50"),
    ],
)
def test_fetch_overseas_hot_rank_normalizes_fields(
    monkeypatch,
    method_name,
    expected_query,
):
    provider = IwencaiProvider()
    received = {}

    def fake_query(query, page_size=50, max_pages=100):
        received.update(
            query=query,
            page_size=page_size,
            max_pages=max_pages,
        )
        return [
            {
                "股票代码": "00700",
                "股票简称": "示例股票",
                "最新价": "100.00",
                "最新涨跌幅": "1.25",
                "个股热度[20260825]": "1",
            }
        ]

    monkeypatch.setattr(provider, "query", fake_query)

    result = getattr(provider, method_name)()

    pd.testing.assert_frame_equal(
        result,
        pd.DataFrame(
            [
                {
                    "symbol": "00700",
                    "name": "示例股票",
                    "price": "100.00",
                    "change_pct": "1.25",
                    "hot_rank": "1",
                }
            ]
        ),
    )
    assert received == {
        "query": expected_query,
        "page_size": 50,
        "max_pages": 100,
    }
