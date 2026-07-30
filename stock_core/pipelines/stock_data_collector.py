from stock_core.database import collections as database
from data.normalizers import canonical_bars_to_system
from data.service import OFFICIAL_SOURCE, fetch_daily_bars
import pandas as pd
from datetime import datetime,timedelta
from stock_core.utils.common import save_to_mongo,load_from_mongodb
from tqdm import tqdm


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

    codes = df["股票代码"].dropna().astype(str).drop_duplicates().tolist()
    # 分批处理
    for i in tqdm(range(0, len(codes), batch_size), desc="拉取股票数据"):
        batch_codes = codes[i:i + batch_size]

        data = fetch_daily_bars(
            OFFICIAL_SOURCE,
            symbols=batch_codes,
            start_date=start_date,
            end_date=end_date,
        )

        if data is not None and not data.empty:
            all_data.append(data)

    # 合并所有批次结果
    if all_data:
        merged = pd.concat(all_data, ignore_index=True)
        return merged.drop_duplicates(
            subset=["symbol", "trade_date", "frequency", "adjustment"]
        ).reset_index(drop=True)
    else:
        return pd.DataFrame()


def main():
    stock_pool = load_from_mongodb(database.stock_pool)
    if stock_pool.empty:
        print("❌ 股票池为空，请先生成股票池数据")
        return

    start_date, end_date = get_date_range(60)
    data = fetch_stock_data(stock_pool, start_date=start_date, end_date=end_date, batch_size=100)
    data = canonical_bars_to_system(data)

    if data is not None and not data.empty:
        save_to_mongo(data,database.stock_history_data)
        print(data)

if __name__ == "__main__":
    main()
