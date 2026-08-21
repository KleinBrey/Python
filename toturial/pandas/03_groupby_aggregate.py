"""Pandas 第 3 课：按股票分组统计。"""

from pathlib import Path

import pandas as pd


csv_path = Path(__file__).parent / "data" / "daily_bars.csv"
bars = pd.read_csv(csv_path, dtype={"symbol": "string"}, parse_dates=["date"])

# groupby 先按 symbol 把数据分组，agg 再对每组做多个统计。
summary = (
    bars.groupby("symbol", as_index=False)
    .agg(
        trading_days=("date", "count"),
        average_close=("close", "mean"),
        highest_close=("close", "max"),
        total_volume=("volume", "sum"),
    )
    .sort_values("total_volume", ascending=False)
)

print("=== 每只股票的汇总 ===")
print(summary.round(2))

# agg 会减少行数；transform 会保留原来的行数，适合给明细增加统计列。
bars["average_volume"] = bars.groupby("symbol")["volume"].transform("mean")
bars["volume_vs_average"] = bars["volume"] / bars["average_volume"]

print("\n=== 每日成交量与自身均量比较 ===")
print(
    bars[["symbol", "date", "volume", "volume_vs_average"]]
    .tail(6)
    .round(2)
)
