from data.normalizers import canonical_stocks_to_system
from data.service import OFFICIAL_SOURCE, fetch_stock_master
from stock_core.database import collections as database
from stock_core.utils.common import show_all_pandas,save_to_mongo

show_all_pandas()

MARKET_CAP_MIN = 30
MARKET_CAP_MAX = 100


def filter_by_stock_type(df):
    """过滤股票类型：排除ST股、科创板、北交所"""
    # 排除ST股票（名称包含ST、*ST、S*ST等）
    df = df[~df['name'].str.contains('ST|退', na=True)]
    # 排除北交所,科创板
    df = df[df["exchange"] != "BJ"]
    df = df[~df["code"].str.startswith(("688", "689", "4", "8"))]
    return df


def filter_by_market_cap(df):
    """过滤市值范围"""
    if "market_cap" not in df or df["market_cap"].isna().all():
        print(
            "⚠️ 扶摇股票基础信息接口尚未提供总市值，本次跳过市值过滤；"
            "统一字段保留为空。"
        )
        return df
    available = df["market_cap"].notna()
    in_range = (df["market_cap"] > MARKET_CAP_MIN) & (df["market_cap"] < MARKET_CAP_MAX)
    return df[~available | in_range]



def get_filtered_stocks():
    # 获取全量A股实时数据
    stock_list = fetch_stock_master()
    # 验证数据是否存在
    if stock_list.empty:
        print("获取数据失败！")
        return

    # 根据条件进行过滤
    filtered_stocks = filter_by_stock_type(stock_list)
    filtered_stocks = filter_by_market_cap(filtered_stocks)
    filtered_stocks = filtered_stocks.drop_duplicates(subset=["symbol"]).copy()

    # 统一层内部使用稳定英文契约，写入旧集合前转换为兼容列名。
    filtered_stocks = canonical_stocks_to_system(filtered_stocks).reset_index(drop=True)

    # 按照新列排序
    filtered_stocks = filtered_stocks[
        ["股票代码", "股票名称", "行业", "每股净资产", "市净率", "总股本(亿)", "总市值(亿)"]
    ]
    print(f"成功从 {OFFICIAL_SOURCE} 获取 {len(filtered_stocks)} 只股票数据")
    return filtered_stocks


def main():
    data = get_filtered_stocks()

    if data is not None and not data.empty:
        save_to_mongo(data,database.stock_pool)
        print(data)

if __name__ == "__main__":
    main()
