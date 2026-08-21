"""
==================================================
综合实战 3：CSV 文件数据分析（csv + statistics + JSON）
==================================================
"""

import csv
import json
from io import StringIO
from statistics import mean

CSV_DATA = """symbol,date,close
600519,2026-08-13,1680
600519,2026-08-14,1688
000001,2026-08-14,10.5
"""

def analyze(csv_text: str) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[float]] = {}
    for row in csv.DictReader(StringIO(csv_text)):
        grouped.setdefault(row["symbol"], []).append(float(row["close"]))
    return {
        symbol: {"min": min(values), "max": max(values), "mean": mean(values)}
        for symbol, values in grouped.items()
    }

def main() -> None:
    result = analyze(CSV_DATA)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""
练习：从命令行接收真实 CSV 路径，并把分析结果写到 summary.json。
"""
