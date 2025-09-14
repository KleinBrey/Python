from mongodb import database
from data_source import tushare
import pandas as pd
from datetime import datetime,timedelta
from utils.common import rename_columns,save_to_mongo,load_from_mongodb
from tqdm import tqdm


COLUMN_MAP = {
    "ts_code": "股票代码",
    "trade_date": "交易日期",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "pre_close": "昨收价",
    "change": "涨跌额",
    "pct_chg": "涨跌幅",
    "vol": "成交量",
    "amount": "成交额"
}


def get_date_range(days: int = 30):
    """
      获取日期范围，默认是过去 `days` 天到今天

      :param days: 回溯天数，默认 30
      :return: (start_date, end_date)，格式 YYYYMMDD
      """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    end_date = end_date.strftime("%Y%m%d")
    start_date = start_date.strftime("%Y%m%d")

    return start_date, end_date


def fetch_stock_data(df, start_date: str, end_date: str, batch_size: int = 10):
    """
    批量拉取股票行情数据，每次最多 batch_size 个股票代码

    :param df: 包含股票代码的 DataFrame（需有列 "股票代码"）
    :param start_date: 开始日期 (YYYYMMDD)
    :param end_date: 结束日期 (YYYYMMDD)
    :param batch_size: 每次请求的股票数量，默认 10
    :return: 拼接后的 DataFrame
    """
    all_data = []

    codes = df["股票代码"].astype(str).tolist()
    # 分批处理
    for i in tqdm(range(0, len(codes), batch_size), desc="拉取股票数据"):
        batch_codes = ",".join(codes[i:i + batch_size])

        data = tushare.daily(
            **{
                "ts_code": batch_codes,
                "start_date": start_date,
                "end_date": end_date,
            },
            fields=[
                "ts_code",
                "trade_date",
                "open",
                "high",
                "low",
                "close",
                "pre_close",
                "change",
                "pct_chg",
                "vol",
                "amount",
            ]
        )

        if data is not None and not data.empty:
            all_data.append(data)

    # 合并所有批次结果
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def main():
    stock_pool = load_from_mongodb(database.stock_pool)
    start_date, end_date = get_date_range(60)
    data = fetch_stock_data(stock_pool, start_date=start_date, end_date=end_date, batch_size=100)
    data =  rename_columns(data,COLUMN_MAP)

    if data is not None and not data.empty:
        save_to_mongo(data,database.stock_history_data)
        print(data)

if __name__ == "__main__":
    main()



