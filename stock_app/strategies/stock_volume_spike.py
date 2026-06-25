"""
股票筛选策略
筛选条件：
今日成交量为过去十日平均成交量的2倍及以上

"""
import pandas as pd
from tqdm import tqdm
from stock_app.database import collections as database
from stock_app.utils.common import show_all_pandas,save_to_mongo,load_from_mongodb

show_all_pandas()

def check_volume_ratio(stock_data: pd.DataFrame, code: str, target_date: str, window: int = 10,
                       threshold: float = 1.0) -> pd.DataFrame:
    """
    检查 target_date 当天成交量是否超过过去 N 日均量的 threshold 倍

    :param stock_data: 包含历史数据的 DataFrame
    :param code: 股票代码
    :param target_date: 目标日期 (格式: 'YYYYMMDD')
    :param window: 回溯天数
    :param threshold: 阈值倍数
    :return: 符合条件的 DataFrame（可能为空）
    """
    # 过滤指定股票
    df_stock = stock_data[stock_data["股票代码"] == code].sort_values(by="交易日期", ascending=True).reset_index(
        drop=True)

    if df_stock.empty:
        print(f"未找到股票 {code} 的历史数据")
        return pd.DataFrame()

    # 取目标日期前 window 天
    df_before = df_stock[df_stock["交易日期"] < target_date].tail(window)
    if df_before.empty:
        print(f"{code} 在 {target_date} 之前没有足够的 {window} 日数据")
        return pd.DataFrame()

    avg_volume = df_before["成交量"].mean()

    # 获取目标日期数据
    df_target = df_stock[df_stock["交易日期"] == target_date].copy()
    if df_target.empty:
        print(f"未找到股票 {code} 在 {target_date} 的数据")
        return pd.DataFrame()

    # 计算均量和量比
    avg_col = f"过去{window}日均量"
    df_target[avg_col] = avg_volume
    df_target["量比"] = df_target["成交量"] / avg_volume

    # 筛选符合条件的
    df_pass = df_target[df_target["量比"] >= threshold].reset_index(drop=True)
    return df_pass


def filter_volume_ratio(df: pd.DataFrame, window: int = 10, threshold: float = 2.0,
                        target_date: str = None) -> pd.DataFrame:
    """
    筛选出指定日期成交量 / 过去N日平均成交量 >= threshold 的股票

    :param df: 股票历史数据 DataFrame，需包含 ["股票代码", "交易日期", "成交量"]
    :param window: 回溯天数，默认 10
    :param threshold: 成交量倍数阈值，默认 2.0
    :param target_date: 指定筛选的日期，格式 "YYYY-MM-DD"，默认是今日
    :return: 符合条件的 DataFrame
    """
    if df.empty:
        return pd.DataFrame()

    df = df.drop_duplicates(subset=["股票代码", "交易日期"]).copy()

    # 默认使用最近交易日
    if target_date is None:
        target_date = df["交易日期"].max()
        print(f"未指定 target_date，自动使用最近交易日 {target_date}")

    results = []
    missing_codes = []

    stock_pool = database.stock_pool.find_many({})
    stock_pool = pd.DataFrame(list(stock_pool))
    unique_codes = stock_pool["股票代码"].dropna().drop_duplicates().tolist()

    for stock_code in tqdm(unique_codes, total=len(unique_codes), desc="正在处理股票"):
        df_pass = check_volume_ratio(df, stock_code, target_date, window, threshold)
        if df_pass is not None and not df_pass.empty:
            results.append(df_pass)
        elif df[df["股票代码"] == stock_code].empty:
            missing_codes.append(stock_code)

    # 合并所有结果
    if results:
        result = pd.concat(results, ignore_index=True)
        result = result.drop_duplicates(subset=["股票代码", "交易日期"]).reset_index(drop=True)
        if missing_codes:
            print(f"⚠️ 有 {len(missing_codes)} 只股票缺少历史数据")
        return result
    else:
        if missing_codes:
            print(f"⚠️ 有 {len(missing_codes)} 只股票缺少历史数据")
        return pd.DataFrame()


def main():
    stock_history_data = load_from_mongodb(database.stock_history_data)
    data = filter_volume_ratio(stock_history_data, 15, 2.0)
    if data is not None and not data.empty:
        save_to_mongo(data,database.stock_filter_result)
        print(data)


if __name__ == "__main__":
    main()
