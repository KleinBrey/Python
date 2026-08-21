"""Pandas 第 0 课：用 Series 和 DataFrame 表示股票数据。"""

import pandas as pd

# Series 是“一列带标签的数据”。这里用交易日期作为标签。
close = pd.Series(
    [1430.0, 1438.0, 1448.0],
    index=["2026-08-13", "2026-08-14", "2026-08-17"],
    name="close",
)

print("=== 贵州茅台收盘价 ===")
print(close)
print("平均收盘价：", close.mean())


# DataFrame 是二维表，也是 Pandas 中最常用的数据结构。
bars = pd.DataFrame(
    {
        "symbol": ["600519.SH", "000001.BJ", "300750.SZ"],
        "name": ["贵州茅台", "平安银行", "宁德时代"],
        "close": [1488.0, 11.4, 300.0],
        "volume": [1680, 11800, 5600],
    }
)

data_list = [
    {
        "symbol": "600519.SH",
        "name": "贵州茅台",
        "close": 1488.0,
        "volume": 1680,
    },
    {
        "symbol": "000001.BJ",
        "name": "平安银行",
        "close": 11.4,
        "volume": 11800,
    },
    {
        "symbol": "300750.SZ",
        "name": "宁德时代",
        "close": 300.0,
        "volume": 5600,
    },
]

data_dict = {
    "symbol": ["600519.SH", "000001.BJ", "300750.SZ"],
    "name": ["贵州茅台", "平安银行", "宁德时代"],
    "close": [1488.0, 11.4, 300.0],
    "volume": [1680, 11800, 5600],
}

bars = pd.DataFrame(data_list)

bars_2 = pd.DataFrame(data_dict)

print(f"两个frame是否相等: {bars.equals(bars_2)}")

print("\n=== 最新行情表 ===")
print(bars)
print("\n行数、列数：", bars.shape)
print("列名：", bars.columns.tolist())
print("收盘价这一列：\n", bars["close"])


# 记住：一列通常是 Series，多列组成 DataFrame。
