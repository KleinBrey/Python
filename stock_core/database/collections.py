from stock_core.database.mongo import MongoDBHelper

# mongoDB 筛选股票池
stock_pool = MongoDBHelper(db_name="python", collection_name="stock_pool")

# mongoDB 获取股票的每日数据
stock_daily_data = MongoDBHelper(db_name="python", collection_name="stock_daily_data")

# mongoDB 缓存股票的历史数据
stock_history_data = MongoDBHelper(db_name="python", collection_name="stock_history_data")

# mongoDB 策略筛选结果
stock_filter_result = MongoDBHelper(db_name="python", collection_name="stock_filter_result")

# mongoDB 同花顺扶摇股票热度排行榜缓存
stock_hot_rankings = MongoDBHelper(db_name="python", collection_name="stock_hot_rankings")
