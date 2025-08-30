from mongodb.mongo import MongoDBHelper

# mongoDB stock_pool
stock_pool = MongoDBHelper(db_name="python", collection_name="stock-pool")

# mongoDB 缓存股票的历史数据
stock_daily_data = MongoDBHelper(db_name="python", collection_name="stock_daily_data")

# mongoDB 策略筛选结果
stock_filter_result = MongoDBHelper(db_name="python", collection_name="stock_filter_result")
