from backend.simple.database import DuckDBDatabase
from backend.simple.provider import HithinkProvider, TushareProvider
from backend.simple.repository import DailyBarRepository, StockRepository
from backend.simple.services import Service

# 初始化数据库
database = DuckDBDatabase()
database.initialize()

# 注册stock表的repository，用来统一处理增删改查
stock_repository = StockRepository(database)
daily_repository = DailyBarRepository(database)

# 注册API调用
hithink_provider = HithinkProvider()

tushare_provider = TushareProvider()

# 业务逻辑处理
service = Service(
    hithink_provider, tushare_provider, stock_repository, daily_repository
)

# 插入股票日线数据
service.update_daily_bar()
