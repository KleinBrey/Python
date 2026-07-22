from __future__ import annotations

import argparse
from datetime import datetime

from stock_core.data_sources.eastmoney_provider import (
    fetch_hk_hot_rank,
    fetch_stock_hot_rank,
    fetch_stock_hot_up,
)


def print_table(title: str, fetcher, page_size: int) -> None:
    print(f"\n=== {title} ===")
    try:
        df = fetcher(page_size=page_size)
    except Exception as exc:
        print(f"抓取失败: {type(exc).__name__}: {exc}")
        return

    if df.empty:
        print("暂无数据")
        return

    print(f"返回 {len(df)} 条，展示前 {min(page_size, len(df))} 条")
    print(df.head(page_size).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="查看东方财富股票热度排行榜")
    parser.add_argument("--limit", type=int, default=20, help="每个榜单展示条数，默认 20")
    args = parser.parse_args()

    page_size = max(1, min(args.limit, 100))
    print(f"东方财富热榜抓取开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_table("东财人气榜", fetch_stock_hot_rank, page_size)
    print_table("东财飙升榜", fetch_stock_hot_up, page_size)
    print_table("东财港股人气榜", fetch_hk_hot_rank, page_size)

    print(f"\n东方财富热榜抓取结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
