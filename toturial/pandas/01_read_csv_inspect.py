"""Pandas 第 1 课：读取日 K CSV，并做第一次数据检查。"""

from pathlib import Path

import pandas as pd

csv_path = Path(__file__).parent / "data" / "daily_bars.csv"


bars = pd.read_csv(
    csv_path,
    dtype={"symbol": "string"},  # 股票代码必须是字符串，保留开头的 0
    parse_dates=["date"],  # 读取时直接把日期转为日期类型
)


print("=== 前 5 行 ===")
print(bars.head())

print("\n=== 表的大小 ===")
print(f"共有 {bars.shape[0]} 行、{bars.shape[1]} 列")

print("\n=== 每列类型和空值情况 ===")
bars.info()

print("\n=== 数值列统计 ===")
print(bars[["open", "high", "low", "close", "volume"]].describe().round(2))

print("\n日期范围：", bars["date"].min().date(), "至", bars["date"].max().date())

# 项目经验：拿到新数据，先看 head、shape、info 和 describe，再开始计算。
