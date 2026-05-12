import akshare as ak
from datetime import datetime

from utils.common import show_all_pandas

show_all_pandas()

SYMBOL = "SZ002402"


def get_search_date() -> str:
    return datetime.today().strftime("%Y%m%d")


def main():
    stock_hot_rank_detail_df = ak.stock_hot_rank_detail_em(symbol=SYMBOL)
    print(stock_hot_rank_detail_df)

    try:
        stock_hot_search_baidu_df = ak.stock_hot_search_baidu(
            symbol="A股",
            date=get_search_date(),
            time="今日",
        )
        print(stock_hot_search_baidu_df)
    except Exception as exc:
        print(f"⚠️ 百度热搜接口调用失败: {exc}")
        print("提示: 这通常是 AkShare 对应接口临时返回了非 JSON 内容，稍后重试即可。")


if __name__ == "__main__":
    main()
