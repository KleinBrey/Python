"""
==================================================
知识点：读取 CSV 与初步检查
==================================================
"""

from io import StringIO

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请运行：python -m pip install pandas")
else:
    csv_text = """symbol,date,open,high,low,close,volume
600519,2026-08-13,1670,1685,1660,1680,1000
600519,2026-08-14,1680,1695,1678,1688,1200
000001,2026-08-14,10.4,10.7,10.3,10.5,5000
"""
    # StringIO 模拟文件，因此案例独立运行；真实项目传 Path 即可。
    frame = pd.read_csv(StringIO(csv_text), parse_dates=["date"], dtype={"symbol": "string"})
    print(frame.head())
    print(frame.info())  # info 直接打印结构并返回 None
    # 先选数值列再 describe，可兼容更多 Pandas 版本且意图清晰。
    print(frame.select_dtypes(include="number").describe())
    print("形状：", frame.shape)

# 股票代码应按字符串读入，否则前导 0 可能消失；日期可用 parse_dates 解析。
# 大文件可用 usecols、dtype、chunksize 控制内存和速度。

"""
本节总结：read_csv 后先检查 head/info/describe；代码列用 string，日期显式解析。
"""
