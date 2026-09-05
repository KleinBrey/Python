"""恐慌下跌 V 字反弹策略。

持续下跌 -> 下跌加速/恐慌放量 -> 反转 K 线 -> 次日确认

"""

from __future__ import annotations

import pandas as pd

from backend.app.provider import TushareProvider

from dataclasses import dataclass

# 恐慌阶段参数
# 统计最近 6 个交易日内的收跌天数。
PANIC_DOWN_WINDOW = 6
# 最近 6 个交易日中至少有 4 天收跌，才视为持续下跌。
PANIC_MIN_DOWN_DAYS = 4
# 当前收盘价相对近 20 日最高价回撤至少 10%，视为深度回撤。
PANIC_DRAWDOWN = -0.10
# 最近 5 日跌幅达到 14 日 ATR 波动率的 2.5 倍，视为快速下跌。
PANIC_ATR_MULTIPLE = 2.5
# 当日成交量至少为此前 20 日均量的 1.5 倍，视为恐慌放量。
PANIC_VOLUME_RATIO = 1.5

# 反转阶段参数
# 长下影或大阳线反转时，成交量至少为此前 20 日均量的 1.3 倍。
REVERSAL_VOLUME_RATIO = 1.3
# 下影线长度至少占当日最高价与最低价区间的 35%。
LONG_WICK_RATIO = 0.35
# 长下影反转 K 线的收盘价至少位于当日振幅区间的 65% 位置。
REVERSAL_CLOSE_POSITION = 0.65
# 大阳线或高开走强 K 线的收盘价至少位于当日振幅区间的 70% 位置。
BIG_BULL_CLOSE_POSITION = 0.70
# 恐慌信号出现后的 3 个交易日内，反转 K 线均可触发反转信号。
PANIC_VALID_DAYS = 3

REQUIRED_COLUMNS = ["symbol", "date", "open", "high", "low", "close", "volume"]

RESULT_COLUMNS = [
    "symbol",
    "name",
    "exchange",
    "market_cap",
    "latest_date",
    "latest_close",
    "latest_1d_pct",
    "latest_5d_pct",
    "volume_ratio",
    "drawdown_20",
    "signal_stage",
    "panic_signal",
    "reversal_signal",
    "confirmed_signal",
    "hot_rank",
    "hot_value",
]


@dataclass(frozen=True, slots=True)
class StrategyConfig:
    """策略参数"""

    # 最小市值 100亿
    min_market_cap: float = 10_000_000_000
    # 最近5天的成交量
    recent_volume_days: int = 5
    # 前20天的成交量
    previous_volume_days: int = 20
    # 最近5个交易日均成交量/最近5个交易日前20个交易日均成交量大于等于1.5
    min_volume_ratio: float = 1.5
    # 最近5日涨幅大于等于5%
    min_return_5d_pct: float = 0.05

    @property
    def required_trading_days(self) -> int:
        # 一共需要25天的数据
        return self.recent_volume_days + self.previous_volume_days


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算收益率、ATR、量比和 K 线形态等基础指标。"""

    result = df.copy()
    previous_close = result["close"].shift(1)

    result["return_1d"] = result["close"].pct_change(fill_method=None)
    result["return_5d"] = result["close"] / result["close"].shift(5) - 1
    # 在最近 6 根 K 线中统计收跌天数，用“下跌密度”过滤单日偶发暴跌。
    result["down_count"] = result["return_1d"].lt(0).rolling(PANIC_DOWN_WINDOW).sum()

    result["high_20"] = result["high"].rolling(20).max()
    result["drawdown_20"] = result["close"] / result["high_20"] - 1

    true_range_1 = result["high"] - result["low"]
    true_range_2 = (result["high"] - previous_close).abs()
    true_range_3 = (result["low"] - previous_close).abs()
    # TR 同时覆盖日内振幅、向上跳空和向下跳空，ATR 才不会低估真实波动。
    result["tr"] = pd.concat([true_range_1, true_range_2, true_range_3], axis=1).max(
        axis=1
    )
    result["atr_14"] = result["tr"].rolling(14).mean()
    result["atr_pct"] = result["atr_14"] / previous_close

    # 均量不包含今天，避免用今天的数据稀释今天的放量程度。
    result["volume_ma20"] = result["volume"].shift(1).rolling(20).mean()
    result["volume_ratio"] = result["volume"] / result["volume_ma20"]

    result["body"] = (result["close"] - result["open"]).abs()
    result["body_pct"] = result["body"] / previous_close
    result["is_bear"] = result["close"] < result["open"]
    result["is_bull"] = result["close"] > result["open"]

    result["body_ma3"] = result["body_pct"].shift(1).rolling(3).mean()
    # 比较基准不含当天，避免大阴线自己抬高均值后反而无法被识别。
    result["large_bear"] = result["is_bear"] & (
        result["body_pct"] >= result["body_ma3"] * 1.3
    )

    # 一字线没有可比较的日内区间，影线比例和收盘位置保持为缺失值。
    candle_range = result["high"] - result["low"]
    result["range"] = candle_range.where(candle_range != 0)
    result["lower_wick"] = result[["open", "close"]].min(axis=1) - result["low"]
    result["lower_wick_ratio"] = result["lower_wick"] / result["range"]
    result["close_position"] = (result["close"] - result["low"]) / result["range"]

    return result


def calculate_panic_signal(df: pd.DataFrame) -> pd.DataFrame:
    """判断行情是否进入持续下跌后的恐慌区。"""

    result = df.copy()
    continuous_drop = result["down_count"] >= PANIC_MIN_DOWN_DAYS
    # 既接受相对 20 日高点的深度回撤，也接受按个股 ATR 标准化后的快速下跌。
    large_drop = (result["drawdown_20"] <= PANIC_DRAWDOWN) | (
        result["return_5d"] <= -result["atr_pct"] * PANIC_ATR_MULTIPLE
    )
    panic_action = (result["volume_ratio"] >= PANIC_VOLUME_RATIO) | result["large_bear"]

    # 三个阶段必须同时成立：持续下跌、跌幅足够、并出现放量或大阴线宣泄。
    result["panic_signal"] = continuous_drop & large_drop & panic_action
    return result


def calculate_reversal_signal(df: pd.DataFrame) -> pd.DataFrame:
    """识别恐慌发生后 3 个交易日内出现的反转 K 线。"""

    result = df.copy()
    previous_close = result["close"].shift(1)

    # 长下影且收在日内高位，表示盘中抛压被承接；放量用于确认承接有效。
    result["long_lower_wick"] = (
        (result["lower_wick_ratio"] >= LONG_WICK_RATIO)
        & (result["close_position"] >= REVERSAL_CLOSE_POSITION)
        & (result["volume_ratio"] >= REVERSAL_VOLUME_RATIO)
    )

    bull_body_pct = (result["close"] - result["open"]) / previous_close
    # 大阳线实体以昨日收盘价归一化，并用 ATR 判断是否显著超过日常波动。
    result["big_bull"] = (
        result["is_bull"]
        & (bull_body_pct >= result["atr_pct"] * 1.2)
        & (result["close_position"] >= BIG_BULL_CLOSE_POSITION)
        & (result["volume_ratio"] >= REVERSAL_VOLUME_RATIO)
    )

    # 收盘站上昨日最高价，比盘中短暂突破更能体现买方持续占优。
    result["strong_reclaim"] = result["is_bull"] & (
        result["close"] > result["high"].shift(1)
    )
    gap_up = result["open"] > previous_close * 1.01
    # 高开后继续收强，排除高开低走造成的假突破。
    result["gap_and_run"] = (
        gap_up
        & result["is_bull"]
        & (result["close_position"] >= BIG_BULL_CLOSE_POSITION)
    )

    result["reversal_bar"] = (
        result["long_lower_wick"]
        | result["big_bull"]
        | result["strong_reclaim"]
        | result["gap_and_run"]
    )

    # shift(1) 确保今天的 panic_signal 不会用于今天自己的反转判断。
    result["recent_panic"] = (
        result["panic_signal"]
        .shift(1)
        .rolling(PANIC_VALID_DAYS)
        .max()
        .fillna(0)
        .astype(bool)
    )
    result["reversal_signal"] = result["recent_panic"] & result["reversal_bar"]
    return result


def calculate_confirmed_signal(df: pd.DataFrame) -> pd.DataFrame:
    """确认反转信号后的下一交易日是否继续走强。"""

    result = df.copy()
    previous_reversal = result["reversal_signal"].shift(1).fillna(False).astype(bool)
    breaks_previous_high = result["close"] > result["high"].shift(1)
    bullish_follow_through = result["is_bull"] & (
        result["close"] >= result["close"].shift(1)
    )

    # 只在反转后的第一根 K 线上确认：突破昨日高点，或阳线收盘不低于昨日。
    result["confirmed_signal"] = previous_reversal & (
        breaks_previous_high | bullish_follow_through
    )
    return result


def run_panic_reversal_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """运行完整策略；多只股票会按 ``symbol`` 分组独立计算。"""

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"日 K 数据缺少字段：{missing_text}")

    if df.empty:
        return df.copy()

    bars = df.copy()
    bars["date"] = pd.to_datetime(bars["date"], errors="raise")
    for column in ["open", "high", "low", "close", "volume"]:
        bars[column] = pd.to_numeric(bars[column], errors="raise")

    def run_one_symbol(symbol_bars: pd.DataFrame) -> pd.DataFrame:
        # 所有 shift/rolling 都必须在单只股票内部按日期计算，禁止跨股票串值。
        result = symbol_bars.sort_values("date").copy()
        result = calculate_indicators(result)
        result = calculate_panic_signal(result)
        result = calculate_reversal_signal(result)
        result = calculate_confirmed_signal(result)
        return result

    results = []
    for _, symbol_bars in bars.groupby("symbol", sort=False, dropna=False):
        results.append(run_one_symbol(symbol_bars))

    return pd.concat(results).sort_values(["symbol", "date"]).reset_index(drop=True)


def show_signals(df: pd.DataFrame) -> None:
    """打印 Panic、Reversal 或 Confirmed 信号及其主要触发原因。"""

    columns = [
        "symbol",
        "date",
        "close",
        "return_5d",
        "drawdown_20",
        "down_count",
        "volume_ratio",
        "panic_signal",
        "long_lower_wick",
        "big_bull",
        "strong_reclaim",
        "gap_and_run",
        "reversal_signal",
        "confirmed_signal",
    ]
    has_signal = df["panic_signal"] | df["reversal_signal"] | df["confirmed_signal"]
    print(df.loc[has_signal, columns].to_string(index=False))


def run_strategy(
    *,
    stocks: pd.DataFrame,
    daily_bars: pd.DataFrame,
    hot_stocks: pd.DataFrame,
    tushare_provider: TushareProvider,
) -> pd.DataFrame:
    """计算最新交易日的恐慌、反转或确认信号。"""

    if daily_bars.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    signals = run_panic_reversal_strategy(
        daily_bars.rename(columns={"trade_date": "date"})
    )
    latest = signals.groupby("symbol", sort=False).tail(1)
    latest = latest[
        latest["panic_signal"] | latest["reversal_signal"] | latest["confirmed_signal"]
    ].rename(
        columns={
            "date": "latest_date",
            "close": "latest_close",
            "return_1d": "latest_1d_pct",
            "return_5d": "latest_5d_pct",
        }
    )
    if latest.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    latest["signal_stage"] = "恐慌"
    latest.loc[latest["reversal_signal"], "signal_stage"] = "反转"
    latest.loc[latest["confirmed_signal"], "signal_stage"] = "确认"

    trade_date = latest["latest_date"].max().strftime("%Y%m%d")
    stock_info = stocks.merge(
        tushare_provider.fetch_daily_basic(trade_date),
        on="symbol",
        how="left",
    )

    hot_stocks = hot_stocks.drop_duplicates("symbol").reset_index(drop=True)
    hot_stocks["hot_rank"] = hot_stocks.index + 1

    return (
        stock_info.merge(latest, on="symbol")
        .merge(hot_stocks[["symbol", "hot_rank", "hot_value"]], on="symbol")
        .sort_values("hot_rank")[RESULT_COLUMNS]
        .reset_index(drop=True)
    )
