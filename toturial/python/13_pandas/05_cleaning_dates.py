"""
==================================================
知识点：缺失值、去重与日期处理
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
            "date": ["2026-08-14", "2026-08-14", "错误日期", "2026-08-15"],
            "close": [1688.0, 1688.0, None, 10.6],
        }
    )
    print("缺失数量：\n", frame.isna().sum())

    frame = frame.drop_duplicates(subset=["symbol", "date"], keep="last")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = frame.groupby("symbol")["close"].transform(
        lambda series: series.fillna(series.median())
    )
    # 某组全为空时中位数仍是 NaN，可按业务决定删除或用全局默认值。
    frame["close"] = frame["close"].fillna(0.0)
    clean = frame.dropna(subset=["date"]).copy()
    clean["year_month"] = clean["date"].dt.to_period("M").astype(str)
    print(clean.sort_values("date"))

# dropna 会删数据，fillna 会引入假设；实际工作必须依据字段含义选择，不要机械处理。

"""
练习：创建 daily_return = close.pct_change()，按 symbol 先分组再计算。

# ==========================
# 参考答案
# ==========================
# frame = frame.sort_values(["symbol", "date"])
# frame["daily_return"] = frame.groupby("symbol")["close"].pct_change()

本节总结：先识别缺失原因再处理；drop_duplicates 需明确业务键；日期用 dt 访问器。
"""
