import akshare as ak


def filter_by_stock_type(df):
    """过滤股票类型：排除ST股、科创板、北交所"""

    # 排除ST股票（名称包含ST、*ST、S*ST等）
    df = df[~df['名称'].str.contains('ST|退', na=False)]

    # 排除北交所,科创板
    df = df[~df['代码'].str.startswith(('8', '4', '688'))]

    # 排除市值低于50亿
    df = df[~(df['流通市值'] > 5000000000)]  # 可选：如果不想要创业板

    return df


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
    filtered_stocks = filter_by_stock_type(stock_list)
    filtered_stocks = filtered_stocks.to_dict(orient='records')
    filtered_stocks = extract_fields(filtered_stocks, ['名称', '代码'])
    return filtered_stocks
