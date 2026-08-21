"""Pandas 第 5 课：清洗缺失值、重复值、错误日期和错误数字。"""

import pandas as pd


# 故意构造几条脏数据，模拟第三方接口或 CSV 中的常见问题。
raw = pd.DataFrame(
    {
        "symbol": ["600519", "600519", "000001", "300750"],
        "date": ["2026-08-20", "2026-08-20", "错误日期", "2026-08-20"],
        "close": [1488.0, 1489.0, "--", None],
        "volume": [1680, 1700, 11800, None],
    }
)

print("=== 原始数据 ===")
print(raw)
print("\n每列缺失数量：\n", raw.isna().sum())

# errors="coerce" 会把无法转换的内容变成 NaN/NaT，方便统一处理。
raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
raw["close"] = pd.to_numeric(raw["close"], errors="coerce")
raw["volume"] = pd.to_numeric(raw["volume"], errors="coerce")

# 本项目 daily_bars 的业务唯一键是 symbol + date，重复时保留最后一条。
clean = raw.drop_duplicates(subset=["symbol", "date"], keep="last")

# 日期和收盘价是分析必需字段，缺失时删除；成交量缺失暂时填 0。
clean = clean.dropna(subset=["date", "close"]).copy()
clean["volume"] = clean["volume"].fillna(0)

print("\n=== 清洗结果 ===")
print(clean.sort_values(["symbol", "date"]))

# 注意：fillna(0) 是业务假设。真实项目中要先确认“缺失”是否真的等于 0。
