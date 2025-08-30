from datetime import datetime, timedelta

import akshare as ak
import pandas as pd


def get_recent_trade_data(
        symbol: str,
        count: int,
) -> pd.DataFrame:
    try:
        # 起始时间从过去的count+10天算起，防止有些天是假期没有数据
        start_date = (datetime.now() - timedelta(days=count + 10)).strftime("%Y%m%d")

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            adjust="qfq"
        )

        # 数据验证
        if df.empty:
            raise ValueError("返回数据为空，请检查股票代码")

        # 根据日期来排序
        df["日期"] = pd.to_datetime(df["日期"])
        df = df.sort_values("日期", ascending=True)

        # 返回最新的10条数据
        return df.head(count).reset_index(drop=True)

    except Exception as e:
        print(f"数据获取失败：{str(e)}")
        return pd.DataFrame()



