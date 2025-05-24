import akshare as ak

from mongo import MongoDBHelper

from filter_stock import get_all_stocks

# mongoDB stock1 集合
stock_db_1= MongoDBHelper(db_name="python", collection_name="stock1")

# mongoDB stock2 集合
stock_db_2 = MongoDBHelper(db_name="python", collection_name="stock2")

stocks = get_all_stocks()

data_list = stocks.to_dict(orient='records')

# stock_db_1.insert_many(data_list)

stock_db_2.insert_many(data_list)
print(data_list,len(data_list))


