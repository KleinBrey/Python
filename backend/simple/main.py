from database import DuckDBDatabase
from provider import Provider
from repository import StockRepository
from services import Service

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 注册stock表的repository，用来统一处理增删改查
operate = StockRepository(database)

# 业务逻辑处理
service = Service(operate)

# 获取API数据
providerInstant = Provider()
stock_list = providerInstant.fetch_stock_list()

# 插入数据
service.update_stocks_list(stock_list)
# operate.insert_stocks(stock_list)

# 数据更新完成以后，再启动 DuckDB UI。
database.start_ui()
