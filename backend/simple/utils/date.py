import pandas as pd


def timestamp_to_date(timestamp_ms: int) -> str:
    """把毫秒时间戳转换为上海时区的 YYYYMMDD 日期。"""

    timestamp = pd.to_datetime(timestamp_ms, unit="ms", utc=True)
    return timestamp.tz_convert("Asia/Shanghai").strftime("%Y%m%d")
