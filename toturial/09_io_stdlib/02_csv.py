"""
==================================================
知识点：csv 标准库
==================================================
"""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory

rows = [
    {"symbol": "600519", "close": 1688.0, "volume": 1200},
    {"symbol": "000001", "close": 10.5, "volume": 5000},
]

with TemporaryDirectory() as directory:
    path = Path(directory) / "prices.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        # newline="" 让 csv 模块统一管理换行，尤其可避免 Windows 空行问题。
        writer = csv.DictWriter(file, fieldnames=["symbol", "close", "volume"])
        writer.writeheader()
        writer.writerows(rows)

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # CSV 读取出的字段默认都是字符串，需要按业务类型转换。
            row["close"] = float(row["close"])
            row["volume"] = int(row["volume"])
            print(row)

"""
本节总结：DictReader/DictWriter 用列名处理数据；读取后要主动转换数字类型。
"""
