"""
==================================================
知识点：DuckDB 与 Pandas DataFrame 配合
==================================================

先安装：python -m pip install duckdb pandas
"""

try:
    import duckdb
    import pandas as pd
except ImportError:
    print("缺少依赖，请运行：python -m pip install duckdb pandas")
else:
    prices_df = pd.DataFrame(
        {
            "symbol": ["600519", "600519", "000001"],
            "date": pd.to_datetime(["2026-08-13", "2026-08-14", "2026-08-14"]),
            "close": [1680.0, 1688.0, 10.5],
        }
    )

    connection = duckdb.connect(":memory:")
    try:
        # register 将现有 DataFrame 暴露为可查询视图，不必先逐行 INSERT。
        connection.register("prices_view", prices_df)
        result_df = connection.execute(
            """
            SELECT symbol, COUNT(*) AS days, AVG(close) AS average_close
            FROM prices_view
            GROUP BY symbol
            ORDER BY average_close DESC
            """
        ).df()
        print(result_df)
    finally:
        connection.close()

# DuckDB 负责 SQL/大规模分析，Pandas 负责交互式清洗与展示，二者可以互补。

"""
练习：查询每个 symbol 的最高 close。

# ==========================
# 参考答案（替换 SQL）
# ==========================
# SELECT symbol, MAX(close) AS max_close FROM prices_view GROUP BY symbol

本节总结：register 让 SQL 查询 DataFrame；.df() 把查询结果返回为 DataFrame。
"""
