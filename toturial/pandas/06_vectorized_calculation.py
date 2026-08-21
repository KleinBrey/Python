"""Pandas 第 6 课：用列运算计算涨跌额、涨跌幅和振幅。"""

from pathlib import Path

import pandas as pd


csv_path = Path(__file__).parent / "data" / "daily_bars.csv"
bars = pd.read_csv(csv_path, dtype={"symbol": "string"}, parse_dates=["date"])
bars = bars.sort_values(["symbol", "date"]).reset_index(drop=True)

# shift(1) 表示把上一行移动到当前行。
# 先 groupby，才能保证取到的是“同一只股票”的前一日收盘价。
bars["pre_close"] = bars.groupby("symbol")["close"].shift(1)

# Pandas 会让整列逐行计算，不需要自己写 for 循环。
bars["change"] = bars["close"] - bars["pre_close"]
bars["return_pct"] = bars["change"] / bars["pre_close"] * 100
bars["amplitude_pct"] = (bars["high"] - bars["low"]) / bars["open"] * 100
bars["is_rising"] = bars["close"] > bars["open"]

columns = [
    "symbol",
    "date",
    "pre_close",
    "close",
    "change",
    "return_pct",
    "amplitude_pct",
    "is_rising",
]

print(bars[columns].round(2).to_string(index=False))

# 每只股票第一行没有“前一日”，所以 pre_close 和 return_pct 为 NaN，这是正常的。
