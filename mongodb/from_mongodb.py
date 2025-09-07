from mongodb import database
import pandas as pd

# data = database.stock_pool.find_many({},['股票名称'])

# data = database.stock_pool.find_many({'股票名称':'四会富仕'},['股票名称'])

# 总市值大于18且只显示股票名称字段
# data = database.stock_pool.find_many({"总市值(亿)": {"$gt": 18}},['股票名称'])

#总市值大于18小于60
data = database.stock_pool.find_many({"$or": [{"总市值(亿)": {"$lt": 18}}, {"总市值(亿)": {"$gt": 60}}]})



df = pd.DataFrame(list(data))


print(df)