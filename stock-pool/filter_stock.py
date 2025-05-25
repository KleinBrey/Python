import akshare as ak


def filter_stocks(stock_df):
    # 排除'ST'的股票
    not_st = ~stock_df['名称'].str.contains('ST')
    # 排除北交所,科创板
    not_bj = ~stock_df['代码'].str.startswith(('8', '4', '688'))
    # 排除市值低于50亿
    not_small_company = stock_df['流通市值'] > 5000000000
    # 组合条件
    return not_st & not_bj & not_small_company


def extract_fields(original_list, selected_fields):
    filtered_list = [{key: item[key] for key in selected_fields} for item in original_list]
    return filtered_list


def get_filtered_stocks():
    # 获取全量A股实时数据
    stock_list = ak.stock_zh_a_spot_em()
    # 验证数据是否存在
    if stock_list.empty:
        print("获取数据失败！")
        return
    # 直接通过布尔索引过滤
    filtered_stocks = stock_list[filter_stocks(stock_list)]
    filtered_stocks = filtered_stocks.to_dict(orient='records')
    filtered_stocks = extract_fields(filtered_stocks, ['名称', '代码'])
    return filtered_stocks
