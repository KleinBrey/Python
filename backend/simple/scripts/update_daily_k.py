from backend.simple.database import DuckDBDatabase
from backend.simple.provider import HithinkProvider, TushareProvider
from backend.simple.repository import DailyBarRepository, StockRepository
from backend.simple.services import Service


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

    print("""
            请选择要执行的任务：

            1. 更新最近 3 日数据，每批 100 只
            2. 更新最近 60 日数据，每批 50 只
            3. 更新最近 365 日数据，每批 10 只
            4. 同步同花顺股票日线数据
            e. 退出
          """)

    choice = input("请输入选项: ").strip()

    match choice:
        case "1":
            service.update_daily_bar(3, 100)

        case "2":
            service.update_daily_bar(60, 50)

        case "3":
            service.update_daily_bar(365, 10)

        case "4":
            service.update_hithink_daily_bar()

        case "e":
            print("退出")

        case _:
            print(f"无效选项: {choice}")


if __name__ == "__main__":
    main()
