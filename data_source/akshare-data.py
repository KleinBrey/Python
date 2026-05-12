import akshare as ak
from utils.common import show_all_pandas

show_all_pandas()

SYMBOL = "SZ002402"
SEARCH_DATE = "20250616"


def main():
    stock_hot_rank_detail_df = ak.stock_hot_rank_detail_em(symbol=SYMBOL)
    print(stock_hot_rank_detail_df)

    stock_hot_search_baidu_df = ak.stock_hot_search_baidu(symbol="A股", date=SEARCH_DATE, time="今日")
    print(stock_hot_search_baidu_df)


if __name__ == "__main__":
    main()
