from database import DuckDBDatabase
from provider import HithinkProvider
from repository import StockRepository, DailyBarRepository
from services import Service

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 注册stock表的repository，用来统一处理增删改查
stock_repository = StockRepository(database)
daily_repository = DailyBarRepository(database)

# 注册API调用
provider = HithinkProvider()

# 业务逻辑处理
service = Service(provider, stock_repository, daily_repository)

# 插入股票列表数据
service.update_stocks_list()

# 插入股票日线数据
# service.update_daily_bar()
