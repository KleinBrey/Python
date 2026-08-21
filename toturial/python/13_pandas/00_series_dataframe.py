"""
==================================================
知识点：Series 与 DataFrame
==================================================

Series 是带索引的一维数据；DataFrame 是带行列标签的二维表格。
先安装：python -m pip install pandas
"""

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请运行：python -m pip install pandas")
else:
    close = pd.Series([1680.0, 1688.0], index=["2026-08-13", "2026-08-14"], name="close")
    print(close)
    print("均价：", close.mean())

    frame = pd.DataFrame(
        {
            "symbol": ["600519", "000001", "300750"],
            "date": ["2026-08-14"] * 3,
            "open": [1680.0, 10.4, 218.0],
            "high": [1695.0, 10.7, 225.0],
            "low": [1678.0, 10.3, 217.5],
            "close": [1688.0, 10.5, 220.0],
            "volume": [1200, 5000, 3200],
        }
    )
    print(frame)
    print("前两行：\n", frame.head(2))
    print("最后两行：\n", frame.tail(2))
    print("列：", frame.columns.tolist())
    print("索引：", frame.index.tolist())
    print("类型：\n", frame.dtypes)

"""
本节总结：Series 是一列，DataFrame 是表；先观察 shape、columns、dtypes 和 head。
"""
