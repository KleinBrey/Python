"""同花顺 Financial API Python client 的本项目适配器。

接口、重试错误码和分页语义来自官方仓库：
https://github.com/HiThink-Tech/Financial-API/tree/main/python
"""

# 启用 Python 3.7+ 的注解字符串化支持（允许在函数签名中使用更灵活的类型提示）
from __future__ import annotations

# 导入日期时间处理模块
from datetime import datetime
# 导入线程本地存储类，用于线程安全的会话管理
from threading import local
# 导入时间睡眠函数，用于实现重试延迟
import time
# 导入类型提示模块
from typing import Any
# 导入时区处理模块
from zoneinfo import ZoneInfo

# 导入 pandas 数据框架库，用于数据处理
import pandas as pd
# 导入 HTTP 请求库
import requests

# 导入本项目的基础市场数据提供者类
from backend.app.providers.base import MarketDataProvider


# 定义上海时区常量
_SHANGHAI = ZoneInfo("Asia/Shanghai")
# 定义需要重试的 API 响应代码集合（这些代码表示临时性错误）
_RETRY_CODES = {4001, 5001, 5002, 5003}


# 自定义异常类，用于表示同花顺 API 错误
class HiThinkApiError(RuntimeError):
    # 初始化方法，接收错误代码、消息和请求 ID
    def __init__(self, code: int, message: str, request_id: str | None = None):
        # 调用父类初始化方法，格式化错误消息
        super().__init__(f"[hithink code={code}] {message} (request_id={request_id})")
        # 保存错误代码
        self.code = code
        # 保存错误消息
        self.message = message
        # 保存 API 请求 ID（用于追踪）
        self.request_id = request_id


# 同花顺市场数据提供者类，继承自 MarketDataProvider 基类
class HiThinkMarketDataProvider(MarketDataProvider):
    # 定义数据源 ID 标识符
    source_id = "hithink-finance"

    # 初始化方法，配置 API 密钥和连接参数
    def __init__(
        self,
        api_key: str,  # 同花顺 API 密钥
        base_url: str = "https://fuyao.aicubes.cn",  # API 基础 URL，默认为官方地址
        *,  # 下面的参数必须以关键字形式传入
        timeout: int = 30,  # HTTP 请求超时时间（秒），默认 30 秒
        request_interval: float = 0.0,  # 请求间隔时间（秒），用于限流，默认无延迟
    ):
        # 保存并清理 API 密钥（去除首尾空格）
        self.api_key = api_key.strip()
        # 保存 API 基础 URL（去除末尾斜杠）
        self.base_url = base_url.rstrip("/")
        # 保存超时时间（至少 1 秒）
        self.timeout = max(1, timeout)
        # 保存请求间隔（至少 0 秒）
        self.request_interval = max(0.0, request_interval)
        # 初始化线程本地存储对象，用于为每个线程维护独立的 HTTP 会话
        self._thread_state = local()

    # 检查 API 配置是否完整有效
    def is_configured(self) -> bool:
        # 验证 API 密钥存在且不包含占位符字符（"*" 和 "\\"）
        return bool(self.api_key and "*" not in self.api_key and "\\" not in self.api_key)

    # 获取所有股票列表的方法
    def list_stocks(self) -> pd.DataFrame:
        # 初始化存储所有行数据的列表
        rows: list[dict[str, Any]] = []
        # 初始化分页偏移量
        offset = 0
        # 定义每页返回的股票数量
        limit = 10_000
        # 循环分页获取所有股票数据
        while True:
            # 调用 API 获取股票列表数据
            data = self._get(
                "/api/meta/tickers/list",  # API 端点路径
                {
                    "exchange": "SH,SZ,BJ",  # 交易所过滤：上海、深圳、北京
                    "asset_type": "a-share",  # 资产类型过滤：A 股
                    "limit": limit,  # 每页数量
                    "offset": offset,  # 分页偏移
                },
            )
            # 从响应数据中获取 item 字段（股票项目列表），如果不存在则返回空列表
            page = data.get("item", [])
            # 将当前页的数据添加到总列表中
            rows.extend(page)
            # 如果本页返回的数据少于限制数，说明已经是最后一页
            if len(page) < limit:
                break
            # 更新偏移量以获取下一页
            offset += limit

        # 使用列表数据创建 DataFrame
        frame = pd.DataFrame(rows)
        # 定义输出 DataFrame 应该包含的列名
        columns = ["symbol", "code", "exchange", "name", "asset_type", "source"]
        # 如果 DataFrame 为空，返回只有列定义的空 DataFrame
        if frame.empty:
            return pd.DataFrame(columns=columns)
        # 检查响应中是否包含 thscode 列（同花顺股票代码）
        if "thscode" not in frame:
            raise ValueError("同花顺证券目录响应缺少 thscode")
        # 如果响应中没有 name 列，则添加一个全为 None 的列
        if "name" not in frame:
            frame["name"] = None
        # 从 thscode 中提取符号，转换为大写（格式：xxxxxx.SH/SZ/BJ）
        frame["symbol"] = frame["thscode"].astype("string").str.upper()
        # 使用正则表达式解析 symbol，提取 6 位代码和交易所信息
        parsed = frame["symbol"].str.extract(r"^(?P<code>\d{6})\.(?P<exchange>SH|SZ|BJ)$")
        # 将提取的代码列添加到 DataFrame
        frame["code"] = parsed["code"]
        # 将提取的交易所列添加到 DataFrame
        frame["exchange"] = parsed["exchange"]
        # 如果响应中没有 asset_type 列，则设定所有行都为 "a-share"
        if "asset_type" not in frame:
            frame["asset_type"] = "a-share"
        # 为所有行添加数据源 ID
        frame["source"] = self.source_id
        # 选择指定列，删除任何必要字段为空的行，去除重复（保留最后一个），排序，重置索引
        return (
            frame[columns]
            .dropna(subset=["symbol", "code", "exchange"])  # 删除 symbol/code/exchange 为空的行
            .drop_duplicates("symbol", keep="last")  # 按 symbol 去重，保留最后一个
            .sort_values("symbol")  # 按 symbol 升序排序
            .reset_index(drop=True)  # 重置索引
        )

    # 获取某个股票在指定日期范围内的日线数据的方法
    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # 规范化股票代码：去除空格并转为大写
        normalized = symbol.strip().upper()
        # 验证代码格式是否正确（必须包含交易所后缀 "."）
        if not normalized or "." not in normalized:
            raise ValueError(f"thscode 必须包含交易所后缀: {symbol!r}")
        # 将起始日期字符串解析为 datetime 对象，并设置为上海时区的开始时刻
        start = datetime.strptime(start_date, "%Y%m%d").replace(tzinfo=_SHANGHAI)
        # 将结束日期字符串解析为 datetime 对象，并设置为上海时区的最后一刻（23:59:59.999）
        end = datetime.strptime(end_date, "%Y%m%d").replace(
            hour=23, minute=59, second=59, microsecond=999000, tzinfo=_SHANGHAI
        )
        # 调用 API 获取历史价格数据
        data = self._get(
            "/api/a-share/prices/historical",  # 历史价格 API 端点
            {
                "thscode": normalized,  # 股票代码
                "interval": "1d",  # 时间间隔：日线
                "start": int(start.timestamp() * 1000),  # 起始时间戳（毫秒）
                "end": int(end.timestamp() * 1000),  # 结束时间戳（毫秒）
                "adjust": "none",  # 不进行复权调整
            },
        )
        # 创建 DataFrame，从响应的 item 字段获取数据
        frame = pd.DataFrame(data.get("item", []))
        # 如果没有返回数据，返回空 DataFrame
        if frame.empty:
            return pd.DataFrame()
        # 重命名列名，以符合项目统一的命名规范
        frame = frame.rename(
            columns={
                "open_price": "open",  # 开盘价
                "high_price": "high",  # 最高价
                "low_price": "low",  # 最低价
                "close_price": "close",  # 收盘价
                "turnover": "amount",  # 成交金额
            }
        )
        # 定义必须的列集合
        required = {"date_ms", "open", "high", "low", "close", "volume"}
        # 找出缺失的列
        missing = required - set(frame.columns)
        # 如果有缺失的列，抛出异常
        if missing:
            raise ValueError(f"同花顺日 K 响应缺少字段: {', '.join(sorted(missing))}")
        # 添加股票符号列
        frame["symbol"] = normalized
        # 将时间戳转换为日期，从 UTC 转换为上海时区，然后去除时区信息并标准化为日期
        frame["trade_date"] = (
            pd.to_datetime(frame["date_ms"], unit="ms", utc=True)  # 将毫秒时间戳转为 UTC 时间
            .dt.tz_convert(_SHANGHAI)  # 转换为上海时区
            .dt.tz_localize(None)  # 去除时区信息
            .dt.normalize()  # 标准化为日期（00:00:00）
        )
        # 处理 OHLCV（开高低收量）和成交额列，确保都是数值类型
        for column in ("open", "high", "low", "close", "volume", "amount"):
            # 如果列不存在，则添加为全 NA 列
            if column not in frame:
                frame[column] = pd.NA
            # 将列转换为数值类型，无法转换的值设为 NaN
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        # 按交易日期排序
        frame = frame.sort_values("trade_date")
        # 计算前收价（前一个交易日的收盘价）
        frame["pre_close"] = frame["close"].shift(1)
        # 计算价格变化（收盘价 - 前收价）
        frame["change"] = frame["close"] - frame["pre_close"]
        # 计算涨跌幅百分比（价格变化 / 前收价 * 100）
        frame["pct_change"] = frame["change"] / frame["pre_close"] * 100
        # 标记复权方式为 "none"（不复权）
        frame["adjustment"] = "none"
        # 标记数据源
        frame["source"] = self.source_id
        # 记录数据导入时间
        frame["ingested_at"] = datetime.now(_SHANGHAI).replace(tzinfo=None)
        # 选择并返回指定顺序的列
        return frame[
            [
                "symbol", "trade_date", "open", "high", "low", "close",
                "pre_close", "change", "pct_change", "volume", "amount",
                "adjustment", "source", "ingested_at",
            ]
        ]

    # 获取或创建线程本地 HTTP 会话的私有方法
    def _session(self) -> requests.Session:
        # 从线程本地存储中尝试获取会话对象
        session = getattr(self._thread_state, "session", None)
        # 如果会话对象不存在，创建一个新的会话
        if session is None:
            session = requests.Session()
            # 将新会话保存到线程本地存储中
            self._thread_state.session = session
        # 返回会话对象
        return session

    # 执行 HTTP GET 请求的私有方法，包含重试逻辑
    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        # 检查 API 是否已配置
        if not self.is_configured():
            raise RuntimeError("缺少 HITHINK_FINANCE_API_KEY")
        # 如果配置了请求间隔，则等待相应的时间
        if self.request_interval:
            time.sleep(self.request_interval)
        # 初始化最后一个错误变量
        last_error: Exception | None = None
        # 最多尝试 3 次请求
        for attempt in range(3):
            try:
                # 发送 GET 请求
                response = self._session().get(
                    f"{self.base_url}{path}",  # 完整 URL
                    # 过滤参数，只保留值不为 None 的参数
                    params={key: value for key, value in params.items() if value is not None},
                    # 设置 API 密钥请求头
                    headers={"X-api-key": self.api_key},
                    # 设置请求超时时间
                    timeout=self.timeout,
                )
                # 检查 HTTP 状态码，如果不是 200-299，抛出异常
                response.raise_for_status()
                # 解析 JSON 响应体
                payload = response.json()
            # 捕获连接错误和超时错误
            except (requests.ConnectionError, requests.Timeout) as exc:
                # 保存错误信息用于最后的异常处理
                last_error = exc
                # 使用指数退避策略等待后重试（2^attempt 秒）
                time.sleep(2**attempt)
                # 继续下一次尝试
                continue
            # 从响应中获取业务状态码，默认为 -1
            code = payload.get("code", -1)
            # 如果状态码为 0，表示请求成功，返回 data 字段或空字典
            if code == 0:
                return payload.get("data") or {}
            # 如果状态码是需要重试的代码且还有重试机会，则重试
            if code in _RETRY_CODES and attempt < 2:
                # 等待后重试
                time.sleep(2**attempt)
                # 继续下一次尝试
                continue
            # 如果状态码不是 0 且不是可重试的错误，抛出 API 错误异常
            raise HiThinkApiError(code, payload.get("message", ""), payload.get("request_id"))
        # 如果循环退出且有网络错误，抛出最后的网络错误
        if last_error:
            raise last_error
        # 如果没有任何错误被抛出，抛出通用错误（这种情况不应该发生）
        raise RuntimeError("同花顺 Financial API 请求失败")
