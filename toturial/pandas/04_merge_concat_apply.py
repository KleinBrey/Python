"""Pandas 第 4 课：合并股票信息、追加新行情、映射分类。"""

from pathlib import Path

import pandas as pd


data_dir = Path(__file__).parent / "data"
stocks = pd.read_csv(data_dir / "stocks.csv", dtype={"symbol": "string"})
bars = pd.read_csv(
    data_dir / "daily_bars.csv",
    dtype={"symbol": "string"},
    parse_dates=["date"],
)

# merge 类似 SQL JOIN：用 symbol 把股票名称合并到日 K 表。
result = bars.merge(
    stocks,
    on="symbol",
    how="left",
    validate="many_to_one",  # 多条日 K 对应一条股票信息
)

print("=== 合并后的数据 ===")
print(result[["symbol", "name", "date", "close"]].head())

# concat 常用于追加新一批行情。这里复制最后三行模拟下一批数据。
new_bars = bars.groupby("symbol", as_index=False).tail(1).copy()
new_bars["date"] = pd.Timestamp("2026-08-21")
all_bars = pd.concat([bars, new_bars], ignore_index=True)
print("\n追加前后行数：", len(bars), "->", len(all_bars))

# 固定的一一对应关系优先使用 map，通常比 apply 更直观。
market_label = {"主板": "大盘", "创业板": "成长"}
result["market_label"] = result["market"].map(market_label).fillna("其他")

# apply 适合不容易直接写成列运算的自定义规则。
result["price_label"] = result["close"].apply(
    lambda price: "高价" if price >= 100 else "普通"
)
print("\n=== 分类结果 ===")
print(result[["name", "market_label", "price_label"]].drop_duplicates())
