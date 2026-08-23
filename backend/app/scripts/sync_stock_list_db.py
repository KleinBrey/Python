from backend.app.database import DuckDBDatabase
from backend.app.provider import HithinkProvider, TushareProvider
from backend.app.repository import StockRepository, DailyBarRepository
from backend.app.services import Service


def main() -> None:

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

    # 插入股票列表数据
    service.update_stocks_list()


if __name__ == "__main__":
    main()
