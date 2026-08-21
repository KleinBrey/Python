"""
==================================================
知识点：groupby 分组聚合
==================================================
"""

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请运行：python -m pip install pandas")
else:
    frame = pd.DataFrame(
        {
            "symbol": ["600519", "600519", "000001", "000001"],
            "date": pd.to_datetime(["2026-08-13", "2026-08-14"] * 2),
            "close": [1680.0, 1688.0, 10.4, 10.5],
            "volume": [1000, 1200, 4800, 5000],
        }
    )

    summary = (
        frame.groupby("symbol", as_index=False)
        .agg(
            average_close=("close", "mean"),
            max_close=("close", "max"),
            total_volume=("volume", "sum"),
            trading_days=("date", "count"),
        )
        .sort_values("average_close", ascending=False)
    )
    print(summary)

    # transform 返回与原表同长度结果，适合给每行增加所属组的统计值。
    frame["symbol_average"] = frame.groupby("symbol")["close"].transform("mean")
    print(frame)

"""
本节总结：groupby 遵循“拆分-应用-合并”；agg 汇总，transform 保持原行数。
"""
