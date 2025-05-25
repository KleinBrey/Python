import akshare as ak
import pandas as pd


def get_all_a_stocks():
    """获取全量A股代码列表（过滤ST股和北交所）"""
    stock_list = ak.stock_zh_a_spot_em()
    # 过滤ST股（名称含'ST'）和北交所股票（代码以8或4开头）
    filtered = stock_list[
        ~stock_list['名称'].str.contains('ST') &
        ~stock_list['代码'].str.startswith(('8', '4'))
        ]
    return filtered['代码'].tolist()


def is_rising_5days(symbol, days):
    """判断个股是否连续5日收盘价上涨"""
    try:
        # 获取后复权日K线数据（前复权用'qfq'）
        df = ak.stock_zh_a_hist(symbol=symbol,
                                start_date=pd.Timestamp.now().strftime("%Y%m%d"),
                                period='daily',
                                adjust='qfq')
        if len(df) < 5:  # 数据不足5天（如新股）跳过
            return False
        # 取最近5天数据并按日期升序排列
        latest_5 = df.tail(5).sort_values('日期')
        closes = latest_5['收盘'].values
        # 检查是否连续递增（每日收盘价 > 前一日）
        return all(closes[i] > closes[i - 1] for i in range(1, 5))
    except Exception as e:
        # print(f"Error processing {symbol}: {e}")
        return False


# 主程序
# all_stocks = get_all_a_stocks()
# rising_stocks = []
#
# # 遍历股票代码（带进度条）
# for symbol in tqdm(all_stocks, desc='筛选进度'):
#     if is_rising_5days(symbol):
#         rising_stocks.append(symbol)
#
# # 输出结果
# result_df = pd.DataFrame(rising_stocks, columns=['股票代码'])
# result_df.to_csv('连续5日上涨个股.csv', index=False)
# print(f"筛选完成！共找到 {len(rising_stocks)} 只符合条件的个股，已保存至 CSV 文件。")
print(1)
