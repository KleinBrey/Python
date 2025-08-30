import akshare as ak
import numpy as np


def filter_by_stock_type(df):
    """过滤股票类型：排除ST股、科创板、北交所"""

    # 排除ST股票（名称包含ST、*ST、S*ST等）
    df = df[~df['名称'].str.contains('ST|退', na=False)]

    # 排除北交所,科创板
    df = df[~df['代码'].str.startswith(('8', '4', '688'))]

    # 排除市值低于50亿
    df = df[~(df['流通市值'] > 5000000000)]  # 可选：如果不想要创业板

    return df


def filter_by_market_cap(df):
    """按市值筛选：30亿 < 市值 < 300亿"""

    # 总市值单位通常是元，需要转换为亿元，四舍五入为整数
    # 先处理缺失值和无穷值
    df['总市值_亿'] = df['总市值'] / 100000000
    df['总市值_亿'] = df['总市值_亿'].fillna(0).replace([np.inf, -np.inf], 0).round().astype(int)

    # 筛选市值在30亿到300亿之间
    df = df[(df['总市值_亿'] > 30) & (df['总市值_亿'] < 300)]

    return df



def get_filtered_stocks():
    # 获取全量A股实时数据
    stock_list = ak.stock_zh_a_spot_em()
    # 验证数据是否存在
    if stock_list.empty:
        print("获取数据失败！")
        return
    # 直接通过布尔索引过滤
    filtered_stocks = filter_by_stock_type(stock_list)
    filtered_stocks = filter_by_market_cap(filtered_stocks)
    filtered_stocks = filtered_stocks[['名称', '代码']]
    print(f"成功获取 {len(filtered_stocks)} 只股票数据")
    return filtered_stocks
