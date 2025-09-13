from mongodb import database
import pandas as pd


def get_stock_history(code: str):
    """获取某个股票代码的所有历史数据"""
    data = database.stock_daily_data.find_many({})
    df = pd.DataFrame(list(data))
    return (
        df[df["股票代码"] == code]
        .sort_values(by="交易日期", ascending=True)
        .reset_index(drop=True)
    )


