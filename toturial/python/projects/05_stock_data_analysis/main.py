"""
==================================================
综合实战 5：股票数据分析（Pandas + DuckDB）
==================================================
"""

def main() -> None:
    try:
        import duckdb
        import pandas as pd
    except ImportError:
        print("缺少依赖，请运行：python -m pip install pandas duckdb")
        return

    frame = pd.DataFrame(
        {
            "symbol": ["600519"] * 3 + ["000001"] * 3,
            "date": pd.to_datetime(["2026-08-12", "2026-08-13", "2026-08-14"] * 2),
            "close": [1660.0, 1680.0, 1688.0, 10.2, 10.4, 10.5],
            "volume": [900, 1000, 1200, 4500, 4800, 5000],
        }
    ).sort_values(["symbol", "date"])

    frame["daily_return"] = frame.groupby("symbol")["close"].pct_change()
    frame["ma_2"] = frame.groupby("symbol")["close"].transform(
        lambda series: series.rolling(2).mean()
    )
    print("明细：\n", frame)

    connection = duckdb.connect(":memory:")
    try:
        connection.register("daily_prices", frame)
        summary = connection.execute(
            """
            SELECT symbol, MIN(close) AS low, MAX(close) AS high,
                   AVG(close) AS average_close, SUM(volume) AS total_volume
            FROM daily_prices GROUP BY symbol ORDER BY average_close DESC
            """
        ).df()
        print("汇总：\n", summary)
    finally:
        connection.close()

if __name__ == "__main__":
    main()
