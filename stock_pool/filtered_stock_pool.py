from data_source import tushare
from mongodb import database
from utils.common import show_all_pandas,rename_columns,save_to_mongo

show_all_pandas()

COLUMN_MAP = {
    "ts_code": "股票代码",
    "name": "股票名称",
    "industry": "行业",
    "bvps": "每股净资产",
    "pb": "市净率",
    "total_share": "总股本(亿)",
    "market_value": "总市值(亿)"
}

MARKET_CAP_MIN = 30
MARKET_CAP_MAX = 100


def filter_by_stock_type(df):
    """过滤股票类型：排除ST股、科创板、北交所"""
    # 排除ST股票（名称包含ST、*ST、S*ST等）
    df = df[~df['name'].str.contains('ST|退', na=True)]
    # 排除北交所,科创板
    df = df[~df['ts_code'].str.endswith('.BJ')]
    df = df[~df['ts_code'].str.startswith(('688', '689', '4', '8'))]
    return df


def filter_by_market_cap(df):
    """过滤市值范围"""
    df = df[(df['market_value'] > MARKET_CAP_MIN) & (df['market_value'] < MARKET_CAP_MAX)]
    return df



def get_filtered_stocks():
    # 获取全量A股实时数据
    stock_list = tushare.bak_basic(**{
        "trade_date": "",
        "ts_code": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "name",
        "industry",
        "total_share",
        "bvps",
        "pb"
    ])
    # 验证数据是否存在
    if stock_list.empty:
        print("获取数据失败！")
        return

    # 计算总市值（保留两位小数）
    stock_list['market_value'] = stock_list['total_share'] * stock_list['pb'] * stock_list['bvps']
    stock_list['market_value'] = stock_list['market_value'].round(2)

    # 根据条件进行过滤
    filtered_stocks = filter_by_stock_type(stock_list)
    filtered_stocks = filter_by_market_cap(filtered_stocks)

    # 转换标题为中文，使用新索引
    filtered_stocks = rename_columns(filtered_stocks,COLUMN_MAP).reset_index(drop=True)

    # 按照新列排序
    filtered_stocks = filtered_stocks[list(COLUMN_MAP.values())]
    print(f"成功获取 {len(filtered_stocks)} 只股票数据")
    return filtered_stocks


def main():
    data = get_filtered_stocks()

    if data is not None and not data.empty:
        save_to_mongo(data,database.stock_pool)
        print(data)

if __name__ == "__main__":
    main()

