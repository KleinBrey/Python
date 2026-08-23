"""A 股日 K 数据同步命令行入口。"""
from __future__ import annotations

import argparse

from backend.app.scripts.sync_daily_k_db import sync_daily_k


def main() -> None:
    """解析回看天数和批大小，然后执行日 K 同步。"""
    parser = argparse.ArgumentParser(description="同步 A 股日 K 到 DuckDB")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=3,
        help="向前同步的自然日数量，默认 3",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="每批股票数量，默认 100",
    )
    args = parser.parse_args()

    if args.lookback_days < 1:
        parser.error("--lookback-days 必须大于 0")
    if args.batch_size < 1:
        parser.error("--batch-size 必须大于 0")

    sync_daily_k(args.lookback_days, args.batch_size)


if __name__ == "__main__":
    main()
