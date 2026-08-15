"""把同花顺 Financial API 的数据转换成项目需要的格式。

官方 Python 示例：
https://github.com/HiThink-Tech/Financial-API/tree/main/python
"""

import time
from datetime import datetime
from threading import local
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from backend.app.providers.base import MarketDataProvider


# 同花顺接口使用中国标准时间。
SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")

# 接口返回这些错误码时，可以稍等一会儿再重试。
RETRYABLE_ERROR_CODES = {4001, 5001, 5002, 5003}


class HiThinkApiError(RuntimeError):
    """同花顺接口返回业务错误时抛出的异常。"""

    def __init__(self, code: int, message: str, request_id: str | None = None):
        error_text = f"[hithink code={code}] {message} (request_id={request_id})"
        super().__init__(error_text)

        # 保存接口返回的原始信息，方便上层代码排查问题。
        self.code = code
        self.message = message
        self.request_id = request_id


class HiThinkMarketDataProvider(MarketDataProvider):
    """从同花顺接口获取股票目录和日 K 数据。"""

    # 数据写入数据库时，会使用这个值标记数据来源。
    source_id = "hithink-finance"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://fuyao.aicubes.cn",
        # 星号后面的参数必须写出参数名，例如 timeout=10。
        *,
        timeout: int = 30,
        request_interval: float = 0.0,
    ):
        """保存接口配置。

        timeout 是请求超时秒数，最小值为 1。
        request_interval 是两次请求之间的等待秒数，最小值为 0。
        """

        # 去掉密钥两端可能误输入的空格。
        self.api_key = api_key.strip()

        # 去掉地址末尾的斜杠，后面拼接接口路径时就不会出现两个斜杠。
        self.base_url = base_url.rstrip("/")

        self.timeout = timeout
        if self.timeout < 1:
            self.timeout = 1

        self.request_interval = request_interval
        if self.request_interval < 0:
            self.request_interval = 0.0

        # 每个工作线程使用自己的 requests.Session，避免线程之间互相影响。
        self._thread_state = local()

    def is_configured(self) -> bool:
        """检查 API 密钥是否已经正确配置。"""

        if not self.api_key:
            return False

        # 配置示例中的隐藏密钥通常含有 * 或反斜杠，不能用于真实请求。
        if "*" in self.api_key:
            return False
        if "\\" in self.api_key:
            return False

        return True

    def list_stocks(self) -> pd.DataFrame:
        """分页获取沪、深、北交易所的全部 A 股。"""

        all_rows: list[dict[str, Any]] = []
        offset = 0
        page_size = 10_000

        # 每次获取一页，直到接口返回的数据少于一页。
        while True:
            request_params = {
                "exchange": "SH,SZ,BJ",
                "asset_type": "a-share",
                "limit": page_size,
                "offset": offset,
            }

            data = self._get("/api/meta/tickers/list", request_params)
            current_page = data.get("item", [])
            all_rows.extend(current_page)

            # 数据不足一页，说明已经到最后一页。
            if len(current_page) < page_size:
                break

            offset = offset + page_size

        frame = pd.DataFrame(all_rows)
        output_columns = [
            "symbol",
            "code",
            "exchange",
            "name",
            "asset_type",
            "source",
        ]

        # 即使接口没有数据，也返回列名完整的空表。
        if frame.empty:
            return pd.DataFrame(columns=output_columns)

        # thscode 是同花顺使用的完整证券代码，例如 600519.SH。
        if "thscode" not in frame:
            raise ValueError("同花顺证券目录响应缺少 thscode")

        # 股票名称不是必需字段。接口未返回时，用空值补齐。
        if "name" not in frame:
            frame["name"] = None

        frame["symbol"] = frame["thscode"].astype("string")
        frame["symbol"] = frame["symbol"].str.upper()

        # 从 600519.SH 中分别取出 600519 和 SH。
        symbol_pattern = r"^(?P<code>\d{6})\.(?P<exchange>SH|SZ|BJ)$"
        parsed_symbol = frame["symbol"].str.extract(symbol_pattern)
        frame["code"] = parsed_symbol["code"]
        frame["exchange"] = parsed_symbol["exchange"]

        if "asset_type" not in frame:
            frame["asset_type"] = "a-share"

        frame["source"] = self.source_id

        # 只保留项目需要的字段。
        result = frame[output_columns]

        # 删除无法识别的证券代码。
        required_columns = ["symbol", "code", "exchange"]
        result = result.dropna(subset=required_columns)

        # 同一个证券代码只保留接口最后返回的记录。
        result = result.drop_duplicates("symbol", keep="last")

        result = result.sort_values("symbol")
        result = result.reset_index(drop=True)
        return result

    def fetch_daily_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """获取一只股票在指定日期范围内的日 K 数据。

        symbol 示例：600519.SH。
        start_date 和 end_date 使用 YYYYMMDD 格式，例如 20260815。
        """

        normalized_symbol = symbol.strip().upper()

        # 同花顺接口要求证券代码包含交易所后缀。
        if not normalized_symbol or "." not in normalized_symbol:
            raise ValueError(f"thscode 必须包含交易所后缀: {symbol!r}")

        # 开始时间是开始日期的 00:00:00（上海时区）。
        start_time = datetime.strptime(start_date, "%Y%m%d")
        start_time = start_time.replace(tzinfo=SHANGHAI_TIMEZONE)

        # 结束时间是结束日期的 23:59:59.999（上海时区）。
        end_time = datetime.strptime(end_date, "%Y%m%d")
        end_time = end_time.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999000,
            tzinfo=SHANGHAI_TIMEZONE,
        )

        # 同花顺接口使用毫秒时间戳。
        start_timestamp_ms = int(start_time.timestamp() * 1000)
        end_timestamp_ms = int(end_time.timestamp() * 1000)

        request_params = {
            "thscode": normalized_symbol,
            "interval": "1d",
            "start": start_timestamp_ms,
            "end": end_timestamp_ms,
            "adjust": "none",
        }
        data = self._get("/api/a-share/prices/historical", request_params)

        rows = data.get("item", [])
        frame = pd.DataFrame(rows)

        if frame.empty:
            return pd.DataFrame()

        # 把接口字段名改成项目统一使用的字段名。
        api_column_names = {
            "open_price": "open",
            "high_price": "high",
            "low_price": "low",
            "close_price": "close",
            "turnover": "amount",
        }
        frame = frame.rename(columns=api_column_names)

        required_columns = ["date_ms", "open", "high", "low", "close", "volume"]
        missing_columns = []

        # 逐个检查接口必须返回的字段。
        for column_name in required_columns:
            if column_name not in frame:
                missing_columns.append(column_name)

        if missing_columns:
            missing_columns.sort()
            missing_text = ", ".join(missing_columns)
            raise ValueError(f"同花顺日 K 响应缺少字段: {missing_text}")

        frame["symbol"] = normalized_symbol

        # 接口时间戳是 UTC 时间，数据库中需要上海当地交易日期。
        utc_time = pd.to_datetime(frame["date_ms"], unit="ms", utc=True)
        shanghai_time = utc_time.dt.tz_convert(SHANGHAI_TIMEZONE)
        local_time = shanghai_time.dt.tz_localize(None)
        frame["trade_date"] = local_time.dt.normalize()

        # 价格、成交量和成交额都转换成数值。
        numeric_columns = ("open", "high", "low", "close", "volume", "amount")
        for column_name in numeric_columns:
            # amount 可能不在接口响应中，所以先补上空列。
            if column_name not in frame:
                frame[column_name] = pd.NA

            # 无法转换的内容会变成 NaN，稍后由服务层统一清理。
            frame[column_name] = pd.to_numeric(
                frame[column_name],
                errors="coerce",
            )

        # 先按交易日期排序，才能正确计算前一个交易日的收盘价。
        frame = frame.sort_values("trade_date")

        frame["pre_close"] = frame["close"].shift(1)
        frame["change"] = frame["close"] - frame["pre_close"]
        frame["pct_change"] = frame["change"] / frame["pre_close"] * 100

        frame["adjustment"] = "none"
        frame["source"] = self.source_id

        # 去掉时区信息，保持与数据库 TIMESTAMP 字段一致。
        current_time = datetime.now(SHANGHAI_TIMEZONE)
        frame["ingested_at"] = current_time.replace(tzinfo=None)

        output_columns = [
            "symbol",
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "pre_close",
            "change",
            "pct_change",
            "volume",
            "amount",
            "adjustment",
            "source",
            "ingested_at",
        ]
        return frame[output_columns]

    def _session(self) -> requests.Session:
        """获取当前线程的 HTTP 会话，没有时就创建一个。"""

        session = getattr(self._thread_state, "session", None)

        if session is None:
            session = requests.Session()
            self._thread_state.session = session

        return session

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """发送 GET 请求，遇到临时错误时最多尝试三次。"""

        if not self.is_configured():
            raise RuntimeError("缺少 HITHINK_FINANCE_API_KEY")

        # 配置了请求间隔时，先等待再发送请求。
        if self.request_interval:
            time.sleep(self.request_interval)

        # 不把值为 None 的参数发送给接口。
        request_params: dict[str, Any] = {}
        for key, value in params.items():
            if value is not None:
                request_params[key] = value

        request_url = f"{self.base_url}{path}"
        request_headers = {"X-api-key": self.api_key}
        last_network_error: Exception | None = None

        # range(3) 会依次得到 0、1、2，所以最多请求三次。
        for attempt in range(3):
            try:
                response = self._session().get(
                    request_url,
                    params=request_params,
                    headers=request_headers,
                    timeout=self.timeout,
                )

                # HTTP 状态码不是 2xx 时，requests 会抛出异常。
                response.raise_for_status()
                payload = response.json()

            except (requests.ConnectionError, requests.Timeout) as error:
                last_network_error = error

                # 第一次等待 1 秒，第二次等待 2 秒，第三次等待 4 秒。
                wait_seconds = 2**attempt
                time.sleep(wait_seconds)
                continue

            response_code = payload.get("code", -1)

            if response_code == 0:
                response_data = payload.get("data")
                return response_data or {}

            # 前两次遇到临时业务错误时，等待后继续重试。
            has_another_attempt = attempt < 2
            should_retry = response_code in RETRYABLE_ERROR_CODES

            if should_retry and has_another_attempt:
                wait_seconds = 2**attempt
                time.sleep(wait_seconds)
                continue

            error_message = payload.get("message", "")
            request_id = payload.get("request_id")
            raise HiThinkApiError(response_code, error_message, request_id)

        # 三次网络请求都失败时，抛出最后一次网络异常。
        if last_network_error is not None:
            raise last_network_error

        # 理论上不会执行到这里，保留异常以防接口行为发生变化。
        raise RuntimeError("同花顺 Financial API 请求失败")
