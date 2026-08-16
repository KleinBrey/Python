from database import DuckDBDatabase
from provider import Provider
from repository import StockRepository

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 注册 stock表的repository，用来统一处理增删改查
operate = StockRepository(database)

# 获取API数据
providerInstant = Provider()
stock_list = providerInstant.fetch_stock_list()

# 插入数据
operate.insert_stocks(stock_list)
