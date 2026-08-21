"""
==================================================
知识点：DuckDB 与 Pandas DataFrame 配合
==================================================

先安装：python -m pip install duckdb pandas
"""

# 同时检查 DuckDB 和 Pandas 是否已经安装。
try:
    import duckdb
    import pandas as pd
except ImportError:
    print("缺少依赖，请运行：python -m pip install duckdb pandas")
else:
    # 创建一个 Pandas DataFrame。
    # DataFrame 可以理解为 Python 中带有行和列的表格。
    prices_df = pd.DataFrame(
        {
            # 同一只股票可以有多个交易日的数据。
            "symbol": ["600519", "600519", "000001"],
            # pd.to_datetime() 把日期字符串转换为 Pandas 日期类型。
            "date": pd.to_datetime(["2026-08-13", "2026-08-14", "2026-08-14"]),
            "close": [1680.0, 1688.0, 10.5],
        }
    )

    # 创建内存数据库。程序结束后，数据库内容会自动消失。
    connection = duckdb.connect(":memory:")

    try:
        # register() 把 prices_df 注册为 DuckDB 可以查询的临时视图。
        # "prices_view" 是这个视图在 SQL 中使用的名字，可以自行修改。
        # 这里不会先把 DataFrame 中的数据逐行 INSERT 到数据库表。
        connection.register("prices_view", prices_df)

        # 使用 SQL 分组统计每只股票的数据。
        result_df = connection.execute("""
            -- COUNT(*) 计算每只股票有多少个交易日。
            -- AVG(close) 计算每只股票的平均收盘价。
            SELECT symbol, COUNT(*) AS days, AVG(close) AS average_close
            FROM prices_view

            -- 将相同 symbol 的数据放在同一组中进行统计。
            GROUP BY symbol

            -- 按平均收盘价从高到低排序。
            ORDER BY average_close DESC
            """).df()

        # .df() 把 DuckDB 查询结果转换成新的 Pandas DataFrame。
        print(result_df)

    finally:
        # 无论查询是否成功，最后都会关闭数据库连接。
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
