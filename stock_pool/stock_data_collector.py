from mongodb import database
from data_source import tushare
import pandas as pd
from datetime import datetime,timedelta


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

def rename_columns(df) :
    """将列名替换为中文"""
    return df.rename(columns=COLUMN_MAP)


def get_date_range(days: int = 30):
    """
      获取日期范围，默认是过去 `days` 天到今天

      :param days: 回溯天数，默认 30
      :return: (start_date_str, end_date_str)，格式 YYYYMMDD
      """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    end_date_str = end_date.strftime("%Y%m%d")
    start_date_str = start_date.strftime("%Y%m%d")

    return start_date_str, end_date_str


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
    for i in range(0, len(codes), batch_size):
        batch_codes = ",".join(codes[i:i + batch_size])
        print(f"🔄 拉取代码: {batch_codes}")

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



def save_to_mongo(df: pd.DataFrame) -> None:
    """保存结果到 MongoDB"""
    try:
        database.stock_history_data.delete_many({})
        database.stock_history_data.insert_many(df.to_dict(orient="records"))
        print("✅ 数据已保存到 MongoDB!")
    except Exception as e:
        print(f"❌ 保存到 MongoDB 失败: {e}")


def main():
    print("=" * 60)
    print("获取股票池股票的历史数据")
    print("=" * 60)
    stock_pool = database.stock_pool.find_many({})
    df = pd.DataFrame(list(stock_pool))
    start_date_str, end_date_str = get_date_range(60)
    data = fetch_stock_data(df, start_date=start_date_str, end_date=end_date_str, batch_size=100)
    data =  rename_columns(data)

    if data is not None and not data.empty:
        save_to_mongo(data)
        print(data)

if __name__ == "__main__":
    main()



