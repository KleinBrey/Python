import mongodb.database as database
from filter_stock import get_filtered_stocks

stocks = get_filtered_stocks()

# 先清除数据集里的老数据，再插入新获取的数据
database.stock_pool.delete_many({})
database.stock_pool.insert_many(stocks)

print(stocks, len(stocks))
