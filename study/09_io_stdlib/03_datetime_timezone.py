"""
==================================================
知识点：date、time、datetime、timedelta 与 zoneinfo
==================================================
"""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

SHANGHAI_ZONE = ZoneInfo("Asia/Shanghai")

today = date.today()
market_open = time(9, 30)
now_shanghai = datetime.now(SHANGHAI_ZONE)
now_utc = datetime.now(timezone.utc)
print(today, market_open, now_shanghai, now_utc)

next_week = today + timedelta(days=7)
one_hour_ago = now_shanghai - timedelta(hours=1)
print(next_week, one_hour_ago)

# strftime：datetime -> str；strptime：str -> datetime。
formatted = now_shanghai.strftime("%Y-%m-%d %H:%M:%S %Z")
parsed = datetime.strptime("2026-08-14 09:30:00", "%Y-%m-%d %H:%M:%S")
print(formatted, parsed)

# parsed 没有 tzinfo，是 naive datetime；加上明确时区后才是 aware datetime。
aware_parsed = parsed.replace(tzinfo=SHANGHAI_ZONE)
print(aware_parsed.astimezone(timezone.utc))

# 实际系统常用 UTC 存储/传输，展示时转换到用户时区。
# 不要把固定 +08:00 当作所有地区规则；ZoneInfo 会处理地区历史/夏令时规则。

"""
本节总结：timedelta 表示时间间隔；strftime 格式化，strptime 解析；业务时间明确时区。
"""
