"""同步每日股票热度。"""

from backend.app.database import DuckDBDatabase
from backend.app.provider import IwencaiProvider
from backend.app.repository import StockHotDailyRepository
from backend.app.services import Service


def main() -> None:

    # 初始化数据库
    database = DuckDBDatabase()
    database.initialize()

    # 注册股票热度 Repository。
    stock_hot_repository = StockHotDailyRepository(database)

    # 注册问财 API。
    iwencai_provider = IwencaiProvider()

    # 业务逻辑处理。
    service = Service(
        iwencai_provider=iwencai_provider,
        stock_hot_repository=stock_hot_repository,
    )

    # 获取并保存当天股票热度。
    service.update_stock_hot_daily()


if __name__ == "__main__":
    main()
