import akshare as ak


def filter_stocks(stock_df):
    # 过滤名称不含'ST'的股票
    not_st = ~stock_df['名称'].str.contains('ST')
    # 过滤代码不以'8'或'4'开头的股票（排除北交所）
    not_bj = ~stock_df['代码'].str.startswith(('8', '4'))
    # 组合条件
    return not_st & not_bj


def get_all_stocks():
    # 获取全量A股实时数据
    stock_list = ak.stock_zh_a_spot_em()
    # 验证数据是否存在
    if stock_list.empty:
        print("获取数据失败！")
        return
    # 直接通过布尔索引过滤
    filtered_stocks = stock_list[filter_stocks(stock_list)]
    return  filtered_stocks

