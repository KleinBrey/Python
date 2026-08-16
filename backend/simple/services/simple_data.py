from repository import StockRepository
from provider import Provider
import pandas as pd
from tqdm.auto import tqdm


class Service:
    def __init__(self, repository: StockRepository, provider: Provider):
        self.repository = repository
        self.provider = provider

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

    def update_stocks_list(self):
        # API 请求数据
        result = self.provider.fetch_stock_list()
        # 格式化清洗数据
        stock_list = self.format_stock_list(result["data"]["item"])
        # 存到数据库
        self.repository.insert_stocks(stock_list)

    def update_daily_bar(self):
        stocks_list_from_db = self.repository.get_table_data()

        for stock in tqdm(
            stocks_list_from_db.itertuples(index=False),
            total=len(stocks_list_from_db),
            desc="同步股票",
        ):
            print(f"{stock.name}")

        print("update daily bar")
