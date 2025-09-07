from mongodb import database
from data_source import tushare

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

database.stock_pool.delete_many({})
database.stock_pool.insert_many(stock_list.to_dict(orient="records"))