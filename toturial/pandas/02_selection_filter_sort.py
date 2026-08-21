"""Pandas 第 2 课：选择、筛选和排序日 K 数据。"""

from pathlib import Path

import pandas as pd


csv_path = Path(__file__).parent / "data" / "daily_bars.csv"
bars = pd.read_csv(csv_path, dtype={"symbol": "string"}, parse_dates=["date"])

# 选择单列得到 Series；选择多列得到 DataFrame。
print("=== 单列 ===")
print(bars["close"].head())

print("\n=== 多列 ===")
print(bars[["symbol", "date", "close"]].head())

# loc 使用行条件和列名，是项目中最常用的选择方式。
maotai = bars.loc[
    bars["symbol"] == "600519",
    ["date", "open", "close", "volume"],
]
print("\n=== 贵州茅台日 K ===")
print(maotai)

# 多个条件分别加括号，用 & 表示“并且”，用 | 表示“或者”。
strong_days = bars.loc[
    (bars["close"] > bars["open"]) & (bars["volume"] >= 5000),
    ["symbol", "date", "open", "close", "volume"],
]
print("\n=== 放量上涨的交易日 ===")
print(strong_days.sort_values("volume", ascending=False))

# iloc 按整数位置取数据：下面表示前 3 行、前 4 列。
print("\n=== iloc 示例 ===")
print(bars.iloc[:3, :4])
