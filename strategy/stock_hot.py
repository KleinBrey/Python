import pandas as pd

import mongodb.database as database
from utils.common import load_from_mongodb, show_all_pandas

show_all_pandas()

DISPLAY_COLUMNS = ["ts_name", "rank", "concept"]


def main():
    stock_hot_ths = load_from_mongodb(database.stock_hot)
    stock_hot_dc = load_from_mongodb(database.stock_hot_dc)
    source_frames = [df for df in [stock_hot_ths, stock_hot_dc] if not df.empty]

    if not source_frames:
        print("❌ 热股数据为空，请先运行热股抓取脚本")
        return

    df_all = pd.concat(source_frames, ignore_index=True)
    df_all = df_all.drop_duplicates(subset=["ts_code", "rank_time"]).copy()

    df_sorted = df_all.sort_values(by=["rank", "rank_time"], ascending=[True, False])
    df_latest = df_sorted.drop_duplicates(subset=["ts_code"], keep="first").reset_index(drop=True)
    print(df_latest[DISPLAY_COLUMNS])


if __name__ == "__main__":
    main()
