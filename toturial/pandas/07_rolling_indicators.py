"""Pandas 第 7 课：按股票计算移动均线和移动均量。"""

from pathlib import Path

import pandas as pd


csv_path = Path(__file__).parent / "data" / "daily_bars.csv"
bars = pd.read_csv(csv_path, dtype={"symbol": "string"}, parse_dates=["date"])
bars = bars.sort_values(["symbol", "date"]).reset_index(drop=True)

# rolling(3) 表示每次使用当前行及前面的 2 行，共 3 个交易日。
# transform 会把计算结果放回原表相同位置。
bars["ma_3"] = bars.groupby("symbol")["close"].transform(
    lambda prices: prices.rolling(3).mean()
)
bars["volume_ma_3"] = bars.groupby("symbol")["volume"].transform(
    lambda volumes: volumes.rolling(3).mean()
)

bars["close_above_ma_3"] = bars["close"] > bars["ma_3"]
bars["volume_ratio_3"] = bars["volume"] / bars["volume_ma_3"]

columns = [
    "symbol",
    "date",
    "close",
    "ma_3",
    "volume",
    "volume_ma_3",
    "volume_ratio_3",
    "close_above_ma_3",
]

print("=== 全部明细 ===")
print(bars[columns].round(2).to_string(index=False))

latest = bars.groupby("symbol", as_index=False).tail(1)
print("\n=== 每只股票的最新指标 ===")
print(latest[columns].round(2).to_string(index=False))

# 前两行不足 3 个交易日，均线为 NaN。也可以使用 rolling(3, min_periods=1)。
