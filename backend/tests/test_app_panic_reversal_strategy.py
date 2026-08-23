from datetime import date, timedelta

import pandas as pd
import pytest

from backend.app.strategy import PanicReversalConfig, PanicReversalStrategy


def _panic_reversal_bars(
    symbol: str = "600001",
    *,
    reversal_volume: float = 250,
    long_lower_shadow_only: bool = False,
    add_confirmation: bool = False,
) -> pd.DataFrame:
    """构造一段先横盘、再连续下跌、最后放量反转的日线。"""

    closes = [100.0] * 20 + [98, 96, 94, 92, 88, 84, 80, 76]
    volumes = [100.0] * 27 + [200.0]

    rows = []
    for index, (close, volume) in enumerate(zip(closes, volumes, strict=True)):
        previous_close = closes[index - 1] if index else close
        open_price = previous_close
        high = max(open_price, close) + 1
        low = min(open_price, close) - 1

        # 最后一个下跌日是一根放量大阴线，用来表示恐慌抛售。
        if index == len(closes) - 1:
            open_price, high, low = 79.0, 80.0, 74.0

        rows.append(
            [
                symbol,
                date(2026, 7, 1) + timedelta(days=index),
                open_price,
                high,
                low,
                close,
                volume,
            ]
        )

    if long_lower_shadow_only:
        # 收盘没有反包或突破昨日高点，只靠“长下影阳线”形成反转形态。
        reversal = [symbol, date(2026, 7, 29), 75.0, 80.0, 69.0, 79.0, reversal_volume]
    else:
        reversal = [symbol, date(2026, 7, 29), 73.0, 84.0, 70.0, 83.0, reversal_volume]
    rows.append(reversal)

    if add_confirmation:
        rows.append([symbol, date(2026, 7, 30), 83.0, 88.0, 72.0, 87.0, 150.0])

    return pd.DataFrame(rows, columns=["symbol", "date", "open", "high", "low", "close", "volume"])


def test_select_finds_high_score_panic_reversal_warning():
    result = PanicReversalStrategy().select(_panic_reversal_bars())

    assert result["symbol"].tolist() == ["600001"]
    assert result.iloc[0]["signal_stage"] == "预警"
    assert result.iloc[0]["total_score"] == 100
    assert result.iloc[0]["return_8d_pct"] < -10
    assert result.iloc[0]["volume_ratio"] >= 1.8


def test_long_lower_shadow_can_be_the_reversal_shape():
    result = PanicReversalStrategy().select(
        _panic_reversal_bars(long_lower_shadow_only=True)
    )

    assert len(result) == 1
    assert bool(result.iloc[0]["long_lower_shadow"])
    assert not bool(result.iloc[0]["bullish_reversal"])
    assert not bool(result.iloc[0]["break_prev_high"])


def test_follow_through_day_is_marked_as_confirmation():
    result = PanicReversalStrategy().select(
        _panic_reversal_bars(add_confirmation=True)
    )

    assert len(result) == 1
    assert result.iloc[0]["date"] == pd.Timestamp("2026-07-30")
    assert result.iloc[0]["signal_stage"] == "确认"
    assert result.iloc[0]["signal_score"] == 100


def test_reversal_without_enough_volume_is_rejected():
    result = PanicReversalStrategy().select(
        _panic_reversal_bars(reversal_volume=120)
    )

    assert result.empty


def test_input_is_not_modified_and_missing_columns_are_reported():
    bars = _panic_reversal_bars()
    original = bars.copy(deep=True)

    PanicReversalStrategy(PanicReversalConfig(min_score=60)).analyze(bars)
    pd.testing.assert_frame_equal(bars, original)

    with pytest.raises(ValueError, match="volume"):
        PanicReversalStrategy().select(bars.drop(columns="volume"))
