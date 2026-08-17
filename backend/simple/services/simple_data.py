from repository import StockRepository, DailyBarRepository
from provider import Provider
import pandas as pd
from tqdm.auto import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class Service:
    def __init__(
        self,
        provider: Provider,
        stock_repository: StockRepository,
        daily_repository: DailyBarRepository,
    ):
        self.provider = provider
        self.stock_repository = stock_repository
        self.daily_repository = daily_repository

    # 格式化股票列表数据
    @staticmethod
    def format_stock_list(value: list) -> pd.DataFrame:
        frame = pd.DataFrame(value)
        columns = ["symbol", "name", "exchange", "type", "source"]
        # 如果 DataFrame 为空，返回只有列定义的空 DataFrame
        if frame.empty:
            return pd.DataFrame(columns=columns)
        # 格式转换
        frame["symbol"] = frame["ticker"]
        # 将提取的代码列添加到 DataFrame
        frame["type"] = "A股"
        frame["source"] = "Hithink"

        # 只保留目标列，并按 columns 中的顺序排列
        return frame[columns].reset_index(drop=True)

    # 格式化日线股票列表数据
    @staticmethod
    def format_daily_list(symbol: str, value: list) -> pd.DataFrame:
        frame = pd.DataFrame(value)
        columns = [
            "symbol",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
            "source",
        ]
        # 如果 DataFrame 为空，返回只有列定义的空 DataFrame
        if frame.empty:
            return pd.DataFrame(columns=columns)
        # 格式转换
        frame["symbol"] = symbol
        frame["date"] = (
            pd.to_datetime(frame["date_ms"], unit="ms", utc=True)
            .dt.tz_convert("Asia/Shanghai")
            .dt.date
        )
        frame["open"] = frame["open_price"].round(2)
        frame["high"] = frame["high_price"].round(2)
        frame["low"] = frame["low_price"].round(2)
        frame["close"] = frame["close_price"].round(2)
        frame["volume"] = frame["volume"]
        frame["amount"] = frame["turnover"]
        frame["source"] = "Hithink"

        # 只保留目标列，并按 columns 中的顺序排列
        return frame[columns].reset_index(drop=True)

    def update_stocks_list(self):
        # API 请求数据
        result = self.provider.fetch_stock_list()
        # 格式化清洗数据
        stock_list = self.format_stock_list(result["data"]["item"])
        # 存到数据库
        self.stock_repository.insert_stocks(stock_list)

    def update_daily_bar(self):
        end = int(time.time() * 1000)

        start = end - 30 * 24 * 60 * 60 * 1000

        stocks_list_from_db = self.stock_repository.get_table_data()

        with ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="daily-bar",
        ) as executor:

            futures = {}

            # 1. 提交所有任务
            for stock in stocks_list_from_db.itertuples(index=False):
                symbol = f"{stock.symbol}.{stock.exchange}"

                future = executor.submit(
                    self.provider.fetch_historical,
                    symbol,
                    start,
                    end,
                )

                futures[future] = symbol

            # 2. 哪个任务先完成，就先处理哪个
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="同步股票日线",
                unit="个",
            ):
                symbol = futures[future]

                try:
                    # API 请求数据
                    result = future.result()
                    # 格式化清洗数据
                    daily_list = self.format_daily_list(
                        symbol.split(".")[0], result["data"]["item"]
                    )
                    # 存到数据库
                    self.daily_repository.upsert_daily_bars(daily_list)

                except Exception as e:
                    tqdm.write(f"{symbol} 获取失败: {e}")

        print("日线股票列表数据更新完成")
