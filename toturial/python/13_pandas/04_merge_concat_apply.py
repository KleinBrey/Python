"""
==================================================
知识点：merge、concat 与 apply
==================================================
"""

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请运行：python -m pip install pandas")
else:
    stocks = pd.DataFrame(
        {"symbol": ["600519", "000001"], "name": ["贵州茅台", "平安银行"]}
    )
    prices = pd.DataFrame(
        {"symbol": ["600519", "000001"], "close": [1688.0, 10.5]}
    )

    merged = stocks.merge(prices, on="symbol", how="left", validate="one_to_one")
    print(merged)

    next_day = pd.DataFrame(
        {"symbol": ["600519", "000001"], "close": [1690.0, 10.6]}
    )
    combined = pd.concat([prices, next_day], ignore_index=True)
    print(combined)

    merged["price_level"] = merged["close"].apply(
        lambda value: "高价股" if value > 100 else "普通价格"
    )
    print(merged)

# merge 类似 SQL JOIN，按键横向关联；concat 沿行或列拼接。
# apply 灵活但常比向量化慢；能用列运算、map、where 时优先它们。

"""
本节总结：merge 按键关联，concat 拼接表，apply 用于难以向量化的自定义逻辑。
"""
