from data_source import tushare as pro
from datetime import datetime

from mongodb import database


def get_trade_date() -> str:
    return datetime.today().strftime("%Y%m%d")


def main():
    df = pro.ths_hot(
        **{
            "trade_date": get_trade_date(),
            "ts_code": "",
            "market": "热股",
            "is_new": "",
            "limit": "",
            "offset": "",
        },
        fields=[
            "trade_date",
            "data_type",
            "ts_code",
            "ts_name",
            "rank",
            "pct_change",
            "current_price",
            "hot",
            "concept",
            "rank_time",
            "rank_reason",
        ],
    )
    print(df)

    if df is not None and not df.empty:
        database.stock_hot.delete_many({})
        database.stock_hot.insert_many(df.to_dict(orient="records"))


if __name__ == "__main__":
    main()
