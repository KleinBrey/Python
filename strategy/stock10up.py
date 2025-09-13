
"""
股票筛选策略
筛选条件：
1. 今日成交量为过去十日平均成交量的2倍及以上

"""

import time
import warnings
from datetime import datetime, timedelta
import numpy as np
import akshare as ak
import pandas as pd

import mongodb.database as database

def filter_volume_ratio(df: pd.DataFrame, window: int = 10, threshold: float = 2.0, target_date: str = None) -> pd.DataFrame:
    """
    筛选出指定日期成交量 / 过去N日平均成交量 >= threshold 的股票

    :param df: 股票历史数据 DataFrame，需包含 ["股票代码", "交易日期", "成交量"]
    :param window: 回溯天数，默认 10
    :param threshold: 成交量倍数阈值，默认 2.0
    :param target_date: 指定筛选的日期，格式 "YYYY-MM-DD"，默认是今日
    :return: 符合条件的 DataFrame
    """
    if df.empty:
        return df

    # 默认使用今天
    if target_date is None:
        target_date = datetime.today().strftime("%Y-%m-%d")

    # 确保日期是升序
    df = df.sort_values(by=["股票代码", "交易日期"])

    avg_col = f"过去{window}日均量"

    # 计算过去N日平均成交量（不包含当天，所以先 shift(1)）
    df[avg_col] = (
        df.groupby("股票代码")["成交量"]
          .transform(lambda x: x.shift(1).rolling(window).mean())
    )

    # 计算量比
    df["量比"] = df["成交量"] / df[avg_col]

    # 筛选指定日期且符合条件的行
    result = df[(df["交易日期"] == target_date) & (df["量比"] >= threshold)].copy()

    # 只保留需要的字段
    # result = result[["股票代码", "股票名称", "成交量"]]

    return result



def save_to_mongo(df: pd.DataFrame) -> None:
    """保存结果到 MongoDB"""
    try:
        database.stock_filter_result.delete_many({})
        database.stock_filter_result.insert_many(df.to_dict(orient="records"))
        print("✅ 数据已保存到 MongoDB!")
    except Exception as e:
        print(f"❌ 保存到 MongoDB 失败: {e}")

def main():
    stock_history_data = database.stock_history_data.find_many({})
    data = pd.DataFrame(list(stock_history_data))
    data = filter_volume_ratio(data)
    if data is not None and not data.empty:
        save_to_mongo(data)
        print(data)

if __name__ == "__main__":
    main()

