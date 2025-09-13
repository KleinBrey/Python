from mongodb import database
import pandas as pd

pd.set_option("display.max_columns", None)  # 显示所有列
pd.set_option("display.max_rows", None)     # 显示所有行
pd.set_option("display.width", None)        # 不自动换行
pd.set_option("display.max_colwidth", None) # 不截断列内容


def get_stock_history(code: str):
    """获取某个股票代码的所有历史数据"""
    data = database.stock_daily_data.find_many({})
    df = pd.DataFrame(list(data))
    return (
        df[df["股票代码"] == code]
        .sort_values(by="交易日期", ascending=True)
        .reset_index(drop=True)
    )


def check_volume_ratio(stock_data: pd.DataFrame, code: str, target_date: str,
                       window: int = 10, threshold: float = 1.0) -> pd.DataFrame:
    """
    检查 target_date 当天成交量是否超过过去 N 日均量的 threshold 倍

    :param stock_data: 包含历史数据的 DataFrame，需包含 ["股票代码", "交易日期", "成交量"]
    :param code: 股票代码
    :param target_date: 目标日期 (格式: 'YYYYMMDD')
    :param window: 回溯天数
    :param threshold: 阈值倍数
    :return: 符合条件的 DataFrame（可能为空）
    """
    # 过滤指定股票
    df_stock = stock_data[stock_data["股票代码"] == code].copy()
    if df_stock.empty:
        raise ValueError(f"未找到股票 {code} 的历史数据")

    # 取目标日期前 window 天
    df_before = df_stock[df_stock["交易日期"] < target_date].tail(window)
    if df_before.empty:
        raise ValueError(f"{code} 在 {target_date} 之前没有足够的 {window} 日数据")

    avg_volume = df_before["成交量"].mean()

    # 获取目标日期数据
    df_target = df_stock[df_stock["交易日期"] == target_date].copy()
    if df_target.empty:
        raise ValueError(f"未找到股票 {code} 在 {target_date} 的数据")

    # 计算均量和量比
    avg_col = f"过去{window}日均量"
    df_target[avg_col] = avg_volume
    df_target["量比"] = df_target["成交量"] / avg_volume

    # 筛选符合条件的
    df_pass = df_target[df_target["量比"] >= threshold].reset_index(drop=True)
    return df_pass


def main():
    code = "300688.SZ"
    target_date = "20250901"
    window = 10
    threshold = 1.0  # 例如要求至少 2 倍

    stock_data = get_stock_history(code)  # 假设返回全量历史数据 DataFrame
    result = check_volume_ratio(stock_data, code, target_date, window, threshold)
    print(result)


if __name__ == "__main__":
    main()

