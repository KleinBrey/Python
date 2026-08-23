"""恐慌杀跌放量反转策略。

这个策略寻找的不是普通的均线上涨趋势，而是价格在短期严重超跌后，
恐慌盘集中释放、买盘突然接手所形成的早期反转。完整路径如下：

    持续下跌 -> 恐慌/加速杀跌 -> 放量止跌 -> 强力反转 -> 后续确认

策略被有意拆成三个相互独立的前置模块：

1. ``decline_condition``：前面确实跌得足够深、足够密集，并处于阶段低位；
2. ``capitulation_condition``：最近几天至少出现过一次大跌和一次异常放量；
3. ``reversal_condition``：当前交易日放量上涨，且 K 线表现出明显承接力量。

只有三个模块同时满足，并且综合评分不低于阈值，才产生“预警”信号。
预警后的若干交易日不破反转日低点、又突破反转日高点，则升级为“确认”。

设计说明：

* 所有滚动指标都只使用当前及历史数据，不读取未来数据，可用于历史回测；
* 不要求 MA5 上穿 MA10，因为均线确认太慢，会错过超跌反弹的第一段行情；
* 大振幅只是评分加分项，不是硬条件，避免漏掉振幅不大但承接很强的反转；
* ``analyze`` 返回每一天的完整中间指标，适合调参和复盘；
* ``select`` 只检查每只股票的最新一根日线，适合每日运行选股。

输入行情的最低字段要求为：
``symbol/date/open/high/low/close/volume``，一行代表一只股票的一个交易日。
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from rich.console import Console
from rich.table import Table

from backend.app.database import DuckDBDatabase
from backend.app.repository import DailyBarRepository, StockRepository
from backend.app.utils.symbol import validate_symbol


# 终端输出统一交给 Rich，直接运行文件时可以看到带颜色、对齐的选股结果。
console = Console()

# 计算 K 线形态需要完整 OHLC，计算量价关系还需要成交量。
# 其他列（例如 amount、source）即使存在也不会参与策略，避免外部字段影响结果。
REQUIRED_COLUMNS = ["symbol", "date", "open", "high", "low", "close", "volume"]

# ``select`` 对外返回的列。这里固定顺序，便于 API、表格和回测代码稳定消费。
# 百分比列以 100 为单位，例如 -12.5 表示下跌 12.5%；volume_ratio 则是倍数。
RESULT_COLUMNS = [
    "symbol",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "return_8d_pct",
    "down_days_8",
    "volume_ratio",
    "return_1d_pct",
    "close_position",
    "decline_score",
    "capitulation_score",
    "reversal_score",
    "total_score",
    "signal_score",
    "signal_stage",
    "long_lower_shadow",
    "bullish_reversal",
    "break_prev_high",
]


@dataclass(frozen=True, slots=True)
class PanicReversalConfig:
    """策略参数。

    比例参数都使用小数，例如 ``-0.10`` 表示下跌 10%，``1.8`` 的量比
    表示当日成交量是 20 日均量的 1.8 倍。修改策略松紧程度时，通常只需
    创建一个新的配置对象，不必改动指标计算代码。

    默认值是一组偏向“宁缺毋滥”的 A 股日线参数。阈值越严格，候选数量
    通常越少；阈值越宽松，越需要结合基本面、市场环境或人工复核。
    """

    # ------------------------------------------------------------------
    # 阶段一：确认前面真的经历了持续下跌，而不是上涨途中普通回调。
    # ------------------------------------------------------------------

    # 累计跌幅和阴线数量的观察窗口，默认查看最近 8 个交易日。
    decline_days: int = 8

    # 8 日中至少 5 日收盘价低于前一日，确保下跌具有连续性和密度。
    min_down_days: int = 5

    # 8 日累计收益率必须 <= -10%；负数越小，要求的跌幅越深。
    max_decline_return: float = -0.10

    # 短、长均线只用来确认弱势背景，不要求在反转日发生金叉。
    short_ma_days: int = 5
    long_ma_days: int = 10

    # 用近 20 日最低价判断股票是否仍处于阶段低位。
    low_window_days: int = 20

    # 当日最低价距离 20 日最低价最多 5%，防止选到高位放量阳线。
    max_distance_from_low: float = 0.05

    # ------------------------------------------------------------------
    # 阶段二：确认近期出现过恐慌抛售，即“跌得快，同时量在放大”。
    # ------------------------------------------------------------------

    # 恐慌事件允许发生在反转当天或之前两天，不强制所有现象同日出现。
    panic_window_days: int = 3

    # 3 日窗口内至少有一天跌幅 <= -4%，代表短期加速杀跌。
    max_panic_return: float = -0.04

    # 3 日窗口内最大量比至少 1.5，代表抛压或换手显著高于常态。
    min_panic_volume_ratio: float = 1.5

    # 3 日内最大振幅达到 5% 可以获得额外分数，但不是入选硬条件。
    min_panic_amplitude: float = 0.05

    # 量比的基准周期：当日成交量 / 近 20 日平均成交量。
    volume_ma_days: int = 20

    # ------------------------------------------------------------------
    # 阶段三：确认今天不只是止跌，而是已经出现主动买盘和反转形态。
    # ------------------------------------------------------------------

    # 当日相对昨收至少上涨 3%，过滤力度太弱的小阳线。
    min_reversal_return: float = 0.03

    # 反转日量比至少 1.8，说明上涨得到真实成交量配合。
    min_reversal_volume_ratio: float = 1.8

    # 收盘位置 = (收盘价 - 最低价) / (最高价 - 最低价)。
    # 0.70 表示收盘位于全天价格区间上方 30%，低位卖盘大多已被收回。
    min_close_position: float = 0.70

    # 下影线至少为实体的 1.5 倍，才视为明显的低位承接。
    min_lower_shadow_body_ratio: float = 1.5

    # 三个阶段总分达到 70 才产生预警。硬条件负责判断“像不像”，
    # 评分负责判断“强不强”，两者同时使用可以减少临界噪声。
    min_score: int = 70

    # 最多观察反转后的 2 个交易日。期间不破反转低点且收盘突破反转高点，
    # 标记为确认信号；设为 0 可完全关闭确认逻辑。
    confirmation_days: int = 2

    def __post_init__(self) -> None:
        """校验各参数之间最基本的约束。

        配置对象一创建就校验，比运行到滚动计算时才出现难懂的 Pandas
        异常更容易定位问题。这里不限制用户采用激进或保守阈值，只阻止
        无法计算或在逻辑上不可能成立的组合。
        """

        positive_integer_fields = {
            "decline_days": self.decline_days,
            "min_down_days": self.min_down_days,
            "short_ma_days": self.short_ma_days,
            "long_ma_days": self.long_ma_days,
            "low_window_days": self.low_window_days,
            "panic_window_days": self.panic_window_days,
            "volume_ma_days": self.volume_ma_days,
        }
        for name, value in positive_integer_fields.items():
            if value <= 0:
                raise ValueError(f"{name} 必须大于 0")

        if self.confirmation_days < 0:
            raise ValueError("confirmation_days 不能小于 0")
        if self.min_down_days > self.decline_days:
            raise ValueError("min_down_days 不能大于 decline_days")
        if not 0 <= self.min_score <= 100:
            raise ValueError("min_score 必须在 0 到 100 之间")


class PanicReversalStrategy:
    """识别恐慌杀跌后的放量反转和后续确认。

    类本身不访问数据库或第三方行情接口，只负责纯粹的 DataFrame 计算。
    因此同一套逻辑既可以用于盘后选股，也可以被回测、API 或定时任务复用。
    """

    def __init__(self, config: PanicReversalConfig | None = None) -> None:
        # 没有传配置时使用经过集中定义的默认参数，避免各方法散落“魔法数字”。
        self.config = config or PanicReversalConfig()

    def analyze(self, daily_bars: pd.DataFrame) -> pd.DataFrame:
        """计算所有股票、所有交易日的指标和信号。

        输入至少需要 ``symbol/date/open/high/low/close/volume`` 七列。
        返回值包含原始行情、中间指标、三个分项得分和最终信号。函数内部
        始终复制数据，不会给调用方传入的 DataFrame 增加列或改变顺序。

        与 ``select`` 的区别是：本方法不会只取最新日，也不会过滤无信号行，
        因而可以直接查看某只股票历史上每次信号形成的过程。
        """

        # 第一步统一输入格式，保证后续滚动计算接收到干净、按时间排列的数据。
        bars = self._prepare_bars(daily_bars)
        if bars.empty:
            return self._empty_analysis_frame()

        # 滚动窗口绝不能跨股票计算，所以必须先按 symbol 拆开。
        analyzed_stocks = [
            self._analyze_one_stock(stock_bars)
            for _, stock_bars in bars.groupby("symbol", sort=False)
        ]
        return pd.concat(analyzed_stocks, ignore_index=True)

    def select(self, daily_bars: pd.DataFrame) -> pd.DataFrame:
        """返回每只股票最新交易日出现的预警或确认信号。

        每只股票只保留时间上最后一根 K 线，再判断该日是否有信号。因此，
        历史上出现过信号、但最新日已失效的股票不会继续留在候选池中。

        结果优先按信号分数从高到低排列，相同分数再按股票代码排列，保证
        多次运行的顺序稳定。返回空结果时仍保留固定字段，方便下游直接使用。
        """

        analysis = self.analyze(daily_bars)
        if analysis.empty:
            return pd.DataFrame(columns=RESULT_COLUMNS)

        # 每个分组已经按日期升序，tail(1) 就是该股票自己的最新交易日。
        latest = analysis.groupby("symbol", sort=False).tail(1)
        selected = latest.loc[latest["signal"], RESULT_COLUMNS]
        return selected.sort_values(
            ["signal_score", "symbol"], ascending=[False, True]
        ).reset_index(drop=True)

    @staticmethod
    def _prepare_bars(daily_bars: pd.DataFrame) -> pd.DataFrame:
        """检查字段、统一类型，并删除无法参与计算的行情。

        清洗规则比较保守：日期/价格/成交量无法解析、价格非正数、成交量
        非正数或最高价低于最低价的行都会被删除。这里不会擅自填充缺失行情，
        因为用前值填充 OHLC 或成交量会制造并不存在的 K 线和交易信号。
        """

        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in daily_bars.columns
        ]
        if missing_columns:
            missing_text = ", ".join(missing_columns)
            raise ValueError(f"日线数据缺少字段：{missing_text}")

        # 只复制必需字段：既保护原始 DataFrame，也隔离无关字段的数据类型问题。
        bars = daily_bars[REQUIRED_COLUMNS].copy()

        # 证券代码统一成项目内部的 6 位格式；日期无效时先转为 NaT，稍后删除。
        bars["symbol"] = bars["symbol"].map(validate_symbol)
        bars["date"] = pd.to_datetime(bars["date"], errors="coerce")

        # 行情源有时会把数字保存为字符串，统一转换成数值后才能安全计算。
        price_and_volume = ["open", "high", "low", "close", "volume"]
        for column in price_and_volume:
            bars[column] = pd.to_numeric(bars[column], errors="coerce")

        # rolling/pct_change 遇到脏数据可能产生难以解释的结果，因此计算前删除。
        bars = bars.dropna(subset=REQUIRED_COLUMNS)
        bars = bars.loc[
            (bars[["open", "high", "low", "close"]] > 0).all(axis=1)
            & (bars["volume"] > 0)
            & (bars["high"] >= bars["low"])
        ]

        # 同一股票同一天有重复数据时，以输入中的最后一条为准，常见场景是
        # 当日行情被再次同步后，新记录应覆盖旧记录。
        return (
            bars.sort_values(["symbol", "date"])
            .drop_duplicates(["symbol", "date"], keep="last")
            .reset_index(drop=True)
        )

    def _analyze_one_stock(self, stock_bars: pd.DataFrame) -> pd.DataFrame:
        """按时间顺序计算一只股票的完整信号。

        四个步骤按照依赖顺序执行：基础指标 -> 阶段条件 -> 强弱评分 -> 信号。
        拆成多个方法是为了让调参或新增形态时不需要修改一整块复杂表达式。
        """

        frame = stock_bars.sort_values("date").copy()
        self._calculate_basic_indicators(frame)
        self._calculate_pattern_conditions(frame)
        self._calculate_scores(frame)
        self._calculate_signals(frame)
        return frame

    def _calculate_basic_indicators(self, frame: pd.DataFrame) -> None:
        """计算收益率、均线、量比、振幅和 K 线几何数据。

        这一层只计算客观数值，不判断股票是否入选。把指标和条件分开后，
        可以在 ``analyze`` 的结果中直接看到原始指标，更容易理解某只股票
        为什么通过或没有通过下一层条件。
        """

        config = self.config
        # shift(1) 表示“上一交易日”。所有 shift 都只向过去取值，不会未来穿越。
        previous_close = frame["close"].shift(1)

        # 单日收益率 = 今日收盘价 / 昨日收盘价 - 1。
        # 同时保留小数版供条件判断、百分数版供表格展示。
        frame["return_1d"] = frame["close"].pct_change(fill_method=None)
        frame["return_1d_pct"] = frame["return_1d"] * 100

        # 区间收益率 = 今日收盘价 / N 个交易日前收盘价 - 1。
        # 默认 N=8，所以 -0.12 表示 8 个交易日累计下跌 12%。
        frame["return_8d"] = (
            frame["close"] / frame["close"].shift(config.decline_days) - 1
        )
        frame["return_8d_pct"] = frame["return_8d"] * 100

        # 将每天是否下跌先变成 True/False，再在最近 N 日窗口内求和。
        # min_periods=N 保证历史数据不足时返回 NaN，而不是用残缺窗口误判。
        frame["down_days_8"] = (
            frame["return_1d"]
            .lt(0)
            .rolling(config.decline_days, min_periods=config.decline_days)
            .sum()
        )
        # MA5 < MA10 说明短期价格仍处于弱势背景。这里故意不要求均线金叉，
        # 因为本策略希望捕捉价格先于均线反转的阶段。
        frame["ma_short"] = frame["close"].rolling(config.short_ma_days).mean()
        frame["ma_long"] = frame["close"].rolling(config.long_ma_days).mean()

        # 取窗口内真实最低价（low），而非最低收盘价，以识别盘中创出的恐慌低点。
        frame["low_window"] = frame["low"].rolling(config.low_window_days).min()

        # 量比 = 当日成交量 / 近 N 日平均成交量。
        # 与策略原始定义一致，分母的 N 日窗口包含当日成交量。因此异常巨量会
        # 略微抬高均量基准，这比“只与此前 N 日相比”的口径稍保守。
        frame["volume_ma"] = frame["volume"].rolling(config.volume_ma_days).mean()
        frame["volume_ratio"] = frame["volume"] / frame["volume_ma"]

        # 振幅 = (最高价 - 最低价) / 昨日收盘价。
        # 以昨收为分母可以比较不同绝对价格股票的日内波动强度。
        frame["amplitude"] = (frame["high"] - frame["low"]) / previous_close

        # 实体长度不区分阴阳；下影线从最低价量到开盘价、收盘价中较低者。
        # clip(lower=0) 用来防御行情源的轻微异常，避免产生负的影线长度。
        frame["body"] = (frame["close"] - frame["open"]).abs()
        frame["lower_shadow"] = (
            frame[["open", "close"]].min(axis=1) - frame["low"]
        ).clip(lower=0)

        # 收盘位置把全天价格范围标准化到 0~1：
        #   0   = 收在最低价；0.5 = 收在区间中部；1 = 收在最高价。
        # 一字线等 high == low 的情况没有可比较区间，按 0 处理，不作为强收盘。
        candle_range = frame["high"] - frame["low"]
        frame["close_position"] = (
            (frame["close"] - frame["low"]) / candle_range.where(candle_range > 0)
        ).fillna(0.0)

    def _calculate_pattern_conditions(self, frame: pd.DataFrame) -> None:
        """根据基础指标判断“下跌、恐慌、反转”三个阶段。

        本方法生成的是硬条件。硬条件回答“结构是否完整”，评分则在下一步
        回答“结构有多强”。最终信号要求结构完整且分数达标。
        """

        config = self.config

        # 阶段一：持续下跌。
        #
        # near_period_low 使用“当日最低价”判断低位。因为 low_window 本身包含
        # 当日，所以创新低时一定满足；未创新低但距离旧低点不超过 5% 也满足。
        frame["near_period_low"] = (
            frame["low"] <= frame["low_window"] * (1 + config.max_distance_from_low)
        )

        # 四个条件各自防止一种常见误判：
        # 1. 累计跌幅过滤小回调；2. 下跌天数过滤单日偶发暴跌；
        # 3. MA5 < MA10 确认弱势背景；4. 接近新低过滤高位放量上涨。
        frame["decline_condition"] = (
            (frame["return_8d"] <= config.max_decline_return)
            & (frame["down_days_8"] >= config.min_down_days)
            & (frame["ma_short"] < frame["ma_long"])
            & frame["near_period_low"]
        )

        # 阶段二：恐慌杀跌。
        #
        # 对最近 3 日分别寻找“最差收益率、最大量比、最大振幅”。三种极值
        # 不必发生在同一天，例如前一天放量暴跌、今天放量反转也是有效路径。
        recent_worst_return = frame["return_1d"].rolling(
            config.panic_window_days
        ).min()
        recent_max_volume_ratio = frame["volume_ratio"].rolling(
            config.panic_window_days
        ).max()
        recent_max_amplitude = frame["amplitude"].rolling(
            config.panic_window_days
        ).max()

        # panic_drop 与 panic_volume 是硬门槛：只跌不放量可能只是阴跌，
        # 只放量不大跌也可能只是普通换手，都不算完整的恐慌释放。
        frame["panic_drop"] = recent_worst_return <= config.max_panic_return
        frame["panic_volume"] = (
            recent_max_volume_ratio >= config.min_panic_volume_ratio
        )
        # 大振幅常见于多空力量激烈交换，因此用于加分；但某些跌停打开后
        # 形成的反转振幅未必达到阈值，所以不把它放入硬条件。
        frame["panic_wide_range"] = (
            recent_max_amplitude >= config.min_panic_amplitude
        )
        frame["capitulation_condition"] = (
            frame["panic_drop"] & frame["panic_volume"]
        )

        # 阶段三：放量反转。策略支持三种形态，满足任意一种即可。
        is_bullish_candle = frame["close"] > frame["open"]

        # 形态 A：长下影阳线。
        # 盘中价格曾被大幅打低，但收盘重新拉回高位；长下影体现低位承接，
        # 阳线和高收盘位置则说明买方不仅接住抛盘，还取得了当日主动权。
        frame["long_lower_shadow"] = (
            is_bullish_candle
            & (
                frame["lower_shadow"]
                >= frame["body"] * config.min_lower_shadow_body_ratio
            )
            & (frame["close_position"] >= config.min_close_position)
        )
        # 形态 B：大阳反包。
        # 当日涨幅至少 4%，且收盘价高于前一日开盘价，表示已经收复前一根
        # K 线的大部分或全部实体。这里采用简明、略宽松的反包定义。
        frame["bullish_reversal"] = (
            (frame["return_1d"] >= 0.04)
            & (frame["close"] > frame["open"].shift(1))
        )
        # 形态 C：收盘突破昨日最高价。这比盘中短暂越过更严格，意味着直到
        # 收盘买方仍把价格维持在昨日全部成交区间之上。
        frame["break_prev_high"] = frame["close"] > frame["high"].shift(1)

        has_reversal_shape = (
            frame["long_lower_shadow"]
            | frame["bullish_reversal"]
            | frame["break_prev_high"]
        )
        # 只有 K 线形态还不够：必须同时上涨至少 3%、成交量至少放大到 1.8 倍，
        # 并收在全天区间上方，避免把缩量小阳线或冲高回落误认为强反转。
        frame["reversal_condition"] = (
            (frame["return_1d"] >= config.min_reversal_return)
            & (frame["volume_ratio"] >= config.min_reversal_volume_ratio)
            & (frame["close_position"] >= config.min_close_position)
            & has_reversal_shape
        )

    def _calculate_scores(self, frame: pd.DataFrame) -> None:
        """计算三个阶段的强度分数，总分最高 100 分。

        分数并不是独立选股条件，而是对已经满足形态结构的股票做二次确认
        和排序。采用离散加分而不是复杂公式，目的是让每一分都能追溯来源。

        分值分配：

        * 前期下跌 ``decline_score``：40 分；
        * 恐慌释放 ``capitulation_score``：25 分；
        * 当日反转 ``reversal_score``：35 分。
        """

        config = self.config

        # 前期下跌最高 40 分：跌幅 20 + 下跌密度 10 + 阶段低位 10。
        # MA5 < MA10 是 decline_condition 的硬门槛，但不重复计分。
        frame["decline_score"] = (
            (frame["return_8d"] <= config.max_decline_return).astype(int) * 20
            + (frame["down_days_8"] >= config.min_down_days).astype(int) * 10
            + frame["near_period_low"].astype(int) * 10
        )

        # 恐慌释放最高 25 分：异常量 15 + 大振幅 10。
        # 大跌本身是 capitulation_condition 的硬门槛，但不重复计分。
        frame["capitulation_score"] = (
            frame["panic_volume"].astype(int) * 15
            + frame["panic_wide_range"].astype(int) * 10
        )

        # 反转强度最高 35 分，使用“基础分 + 强化分”的阶梯结构：
        #   涨幅 >= 3% 得 10 分，达到 4% 再加 5 分；
        #   量比 >= 1.8 得 5 分，达到 2.0 再加 5 分；
        #   收盘位置 >= 0.70 得 3 分，达到 0.80 再加 2 分；
        #   收盘突破昨日最高价再加 5 分。
        # 这样刚过基础门槛的形态可以入围，但真正强势的反转会排在前面。
        frame["reversal_score"] = (
            (frame["return_1d"] >= config.min_reversal_return).astype(int) * 10
            + (frame["return_1d"] >= 0.04).astype(int) * 5
            + (frame["volume_ratio"] >= config.min_reversal_volume_ratio).astype(int)
            * 5
            + (frame["volume_ratio"] >= 2.0).astype(int) * 5
            + (frame["close_position"] >= config.min_close_position).astype(int) * 3
            + (frame["close_position"] >= 0.80).astype(int) * 2
            + frame["break_prev_high"].astype(int) * 5
        )

        # 三项直接相加，理论最大值严格等于 100，方便阅读和设置阈值。
        frame["total_score"] = (
            frame["decline_score"]
            + frame["capitulation_score"]
            + frame["reversal_score"]
        )

    def _calculate_signals(self, frame: pd.DataFrame) -> None:
        """生成最早的预警信号，并检查随后是否出现确认信号。

        “预警”价格通常更低、更及时，但失败概率也更高；“确认”要求市场
        继续给出突破证据，确定性相对更高，但买入价格通常也会更高。本方法
        同时保留两种阶段，让调用方自行决定使用哪一种。
        """

        config = self.config
        # 预警必须同时满足三段行情结构，不能只凭高分绕过某个阶段。
        # 例如高位放量大阳线即使反转分很高，也会因为缺少前期下跌而被排除。
        frame["early_signal"] = (
            frame["decline_condition"]
            & frame["capitulation_condition"]
            & frame["reversal_condition"]
            & (frame["total_score"] >= config.min_score)
        )

        # 确认逻辑逐一检查反转后的第 1 日、第 2 日……直到配置上限。
        # 以 confirmation_days=2 为例：
        #   lag=1 检查“昨天预警、今天确认”；
        #   lag=2 检查“前天预警、昨天和今天都守住低点、今天确认”。
        confirmation_candidates: list[pd.Series] = []
        confirmation_scores: list[pd.Series] = []
        for days_after_reversal in range(1, config.confirmation_days + 1):
            # shift(lag) 把反转日的低点、高点和分数移动到待确认日进行比较。
            reversal_low = frame["low"].shift(days_after_reversal)

            # 不只检查确认当天，还检查反转日至确认日之间的每一天，确保期间
            # 从未跌破反转日低点。offset=0 是确认日，offset=1 是前一交易日。
            stayed_above_reversal_low = pd.Series(True, index=frame.index)
            for offset in range(days_after_reversal):
                stayed_above_reversal_low &= frame["low"].shift(offset) >= reversal_low

            # 一个有效确认日必须同时满足：
            # 1. lag 日前确实产生过预警；
            # 2. 中间所有低点都守住反转低点；
            # 3. 当前收盘突破反转日最高价；
            # 4. 当前为阳线，避免用冲高回落的阴线确认。
            candidate = (
                frame["early_signal"].shift(days_after_reversal, fill_value=False)
                & stayed_above_reversal_low
                & (frame["close"] > frame["high"].shift(days_after_reversal))
                & (frame["close"] > frame["open"])
            )
            confirmation_candidates.append(candidate)
            confirmation_scores.append(
                frame["total_score"].shift(days_after_reversal).where(candidate)
            )

        # 同一天可能理论上确认不同历史预警，any 表示只要其中一个成立即可；
        # 分数则取对应反转信号中的最高值。
        if confirmation_candidates:
            frame["confirmed_signal"] = pd.concat(
                confirmation_candidates, axis=1
            ).any(axis=1)
            confirmed_score = pd.concat(confirmation_scores, axis=1).max(axis=1)
        else:
            frame["confirmed_signal"] = False
            confirmed_score = pd.Series(float("nan"), index=frame.index)

        # 对外统一 signal 字段，调用方无需自己合并预警池和确认池。
        frame["signal"] = frame["early_signal"] | frame["confirmed_signal"]
        frame["signal_stage"] = ""
        frame.loc[frame["early_signal"], "signal_stage"] = "预警"

        # 如果当天既产生新的预警、又确认了前面的预警，优先显示“确认”，
        # 因为确认代表更成熟的阶段。
        frame.loc[frame["confirmed_signal"], "signal_stage"] = "确认"

        # 确认日自身通常不再满足“8 日深跌 + 恐慌放量”等早期结构，若用确认
        # 当天 total_score 排序会不公平。因此 signal_score 沿用原反转日得分，
        # 让预警股和确认股能够按同一套反转强度尺度比较。
        frame["signal_score"] = frame["total_score"].astype(float)
        frame.loc[frame["confirmed_signal"], "signal_score"] = confirmed_score

    @staticmethod
    def _empty_analysis_frame() -> pd.DataFrame:
        """返回字段稳定的空分析结果。

        即使输入没有有效行情，下游代码仍可安全访问常用指标列，而不必先为
        每一列做存在性判断。这里列出的是对外最常使用的字段；非空分析结果
        还会包含全部内部诊断字段。
        """

        extra_columns = [
            "return_1d",
            "return_1d_pct",
            "return_8d",
            "return_8d_pct",
            "down_days_8",
            "volume_ratio",
            "close_position",
            "decline_score",
            "capitulation_score",
            "reversal_score",
            "total_score",
            "signal_score",
            "signal_stage",
            "signal",
        ]
        return pd.DataFrame(columns=REQUIRED_COLUMNS + extra_columns)


def _build_result_table(selected: pd.DataFrame) -> Table:
    """把策略结果转换成适合终端阅读的中文表格。

    这里仅负责展示，不参与任何选股计算。显示字段优先选择最能解释入选原因的
    指标，完整的技术指标仍然保留在 ``selected`` DataFrame 中。
    """

    table = Table(title="恐慌杀跌放量反转策略结果", header_style="bold cyan")
    table.add_column("股票代码", style="cyan", no_wrap=True)
    table.add_column("股票名称", no_wrap=True)
    table.add_column("交易日", no_wrap=True)
    table.add_column("阶段", justify="center", no_wrap=True)
    table.add_column("收盘价", justify="right")
    table.add_column("8日涨跌", justify="right")
    table.add_column("当日涨跌", justify="right")
    table.add_column("量比", justify="right")
    table.add_column("收盘位置", justify="right")
    table.add_column("分数", justify="right", style="bold green")

    for row in selected.itertuples(index=False):
        # signal_score 在确认日沿用原反转日得分，因此预警和确认可以直接比较。
        stock_name = getattr(row, "name", None)
        display_name = (
            "--" if pd.isna(stock_name) or stock_name == "" else str(stock_name)
        )
        table.add_row(
            str(row.symbol),
            display_name,
            pd.Timestamp(row.date).strftime("%Y-%m-%d"),
            str(row.signal_stage),
            f"{row.close:.2f}",
            f"{row.return_8d_pct:+.2f}%",
            f"{row.return_1d_pct:+.2f}%",
            f"{row.volume_ratio:.2f}",
            f"{row.close_position:.0%}",
            f"{row.signal_score:.0f}",
        )

    return table


def main() -> None:
    """从本地 DuckDB 读取行情、运行策略并在终端打印结果。

    推荐在项目根目录执行：

    ``python -m backend.app.strategy.panic_reversal``

    也可以直接执行文件：

    ``python backend/app/strategy/panic_reversal.py``

    本入口只读取本地数据库，不会请求 Tushare 等外部接口，也不会修改数据库。
    如果没有候选股票，会区分“历史日线不足”和“当前没有符合条件的股票”。
    """

    config = PanicReversalConfig()
    strategy = PanicReversalStrategy(config)
    database = DuckDBDatabase()

    console.rule("[bold cyan]恐慌杀跌放量反转策略[/bold cyan]")
    with console.status("[bold green]正在读取本地行情..."):
        # Repository 使用只读查询取得股票名称和全部日线；策略本身仍然只依赖
        # daily_bars，股票表仅用于让终端结果更容易辨认。
        daily_bars = DailyBarRepository(database).get_table_data()
        stocks = StockRepository(database).get_table_data()

    if daily_bars.empty:
        console.print("[yellow]本地数据库没有日线数据，请先同步行情。[/yellow]")
        return

    latest_trade_date = pd.to_datetime(daily_bars["date"], errors="coerce").max()
    trading_day_count = daily_bars["date"].nunique()
    stock_count = daily_bars["symbol"].nunique()

    console.print(
        "[dim]行情概况：[/dim]"
        f"最新交易日 {latest_trade_date:%Y-%m-%d}，"
        f"共 {stock_count} 只股票、{trading_day_count} 个交易日"
    )

    # 至少需要 20 根日线才能得到完整的 20 日低点和 20 日均量；
    # decline_days + 1 是因为计算 8 日区间收益率需要今天和 8 日前两个端点。
    required_trading_days = max(
        config.low_window_days,
        config.volume_ma_days,
        config.long_ma_days,
        config.decline_days + 1,
    )
    if trading_day_count < required_trading_days:
        console.print(
            "[yellow]暂无结果：历史日线不足。[/yellow]"
            f"当前只有 {trading_day_count} 个交易日，"
            f"策略至少需要 {required_trading_days} 个交易日。"
        )
        return

    with console.status("[bold green]正在计算全市场反转信号..."):
        # select 最终只检查每只股票的最新日，因此不必把整段历史都交给策略。
        # 为了能够识别“前两天预警、今天确认”，在基础 20 日窗口之外额外保留
        # confirmation_days 根 K 线。这样数据库历史再长，直接运行也不会越来越慢。
        calculation_window = required_trading_days + config.confirmation_days
        calculation_bars = (
            daily_bars.sort_values(["symbol", "date"])
            .groupby("symbol", sort=False)
            .tail(calculation_window)
        )
        selected = strategy.select(calculation_bars)

        if not selected.empty and not stocks.empty:
            stock_information_columns = [
                column
                for column in ["symbol", "name", "market", "type"]
                if column in stocks.columns
            ]
            stock_information = stocks[stock_information_columns].drop_duplicates(
                "symbol", keep="last"
            )
            selected = selected.merge(stock_information, on="symbol", how="left")

    if selected.empty:
        console.print("[yellow]最新交易日没有股票符合策略条件。[/yellow]")
        return

    console.print(_build_result_table(selected))
    console.print(f"[bold green]共筛选出 {len(selected)} 只股票。[/bold green]")


if __name__ == "__main__":
    main()
