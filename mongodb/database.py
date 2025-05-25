from mongodb.mongo import MongoDBHelper

# mongoDB stock_pool
stock_pool = MongoDBHelper(db_name="python", collection_name="stock-pool")

# mongoDB stock_daily_data 集合
stock_daily_data = MongoDBHelper(db_name="python", collection_name="stock_daily_data")
