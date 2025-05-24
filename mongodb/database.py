from mongodb.mongo import MongoDBHelper


# mongoDB stock1 集合
stock_pool= MongoDBHelper(db_name="python", collection_name="stock-pool")

# mongoDB stock2 集合
stock_db_2 = MongoDBHelper(db_name="python", collection_name="stock2")