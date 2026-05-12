from data_source import tushare as pro
from mongodb import database
from datetime import datetime

from utils.common import save_to_mongo, show_all_pandas

show_all_pandas()

def get_trade_date() -> str:
    return datetime.today().strftime("%Y%m%d")


def save_dc_hot_stock():
    # 拉取数据
    df = pro.dc_hot(**{
        "trade_date": get_trade_date(),
        "ts_code": "",
        "market": "A股市场",
        "hot_type": "人气榜",
        "is_new": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "trade_date",
        "data_type",
        "ts_code",
        "ts_name",
        "rank",
        "pct_change",
        "current_price",
        "hot",
        "concept",
        "rank_time"
    ])

    df_sorted = df.sort_values(by=["rank", "rank_time"], ascending=[True, False])
    df_latest = df_sorted.drop_duplicates(subset=["ts_code"], keep="first").reset_index(drop=True)

    return df_latest


def main():
    data = save_dc_hot_stock()

    if data is not None and not data.empty:
        save_to_mongo(data, database.stock_hot_dc)
        print(data)

if __name__ == "__main__":
    main()
