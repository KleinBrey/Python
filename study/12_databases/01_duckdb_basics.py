"""
==================================================
知识点：DuckDB 创建连接、建表、插入与查询
==================================================

DuckDB 是面向分析的嵌入式数据库，擅长列式分析和直接查询 CSV/Parquet。
先安装：python -m pip install duckdb
"""

try:
    import duckdb
except ImportError:
    print("缺少 duckdb，请运行：python -m pip install duckdb")
else:
    connection = duckdb.connect(":memory:")
    try:
        connection.execute(
            "CREATE TABLE prices(symbol VARCHAR, trade_date DATE, close DOUBLE)"
        )
        connection.executemany(
            "INSERT INTO prices VALUES (?, ?, ?)",
            [
                ("600519", "2026-08-13", 1680.0),
                ("600519", "2026-08-14", 1688.0),
                ("000001", "2026-08-14", 10.5),
            ],
        )
        result = connection.execute(
            """
            SELECT symbol, AVG(close) AS average_close
            FROM prices
            GROUP BY symbol
            ORDER BY average_close DESC
            """
        ).fetchall()
        print(result)
    finally:
        connection.close()

"""
本节总结：DuckDB 无需独立服务器，适合本地分析；业务交易系统通常选择事务型数据库。
"""
