from data_source import tushare as pro
from mongodb import database


# 拉取数据
df = pro.margin(**{
    "trade_date": "",
    "exchange_id": "",
    "start_date": "",
    "end_date": "",
    "limit": "",
    "offset": ""
}, fields=[
    "trade_date",
    "exchange_id",
    "rzye",
    "rzmre",
    "rzche",
    "rqye",
    "rqmcl",
    "rzrqye",
    "rqyl"
])
print(df)

database.stock_daily_data.delete_many({})
database.stock_daily_data.insert_many(df.to_dict(orient="records"))