from repository import StockRepository
import pandas as pd


class Service:
    def __init__(
        self,
        repository: StockRepository,
    ):
        self.repository = repository

    def update_stocks_list(self, data: pd.DataFrame):
        self.repository.insert_stocks(data)
