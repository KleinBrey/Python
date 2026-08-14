"""A 股市场数据同步脚本。

本脚本用于将同花顺的日 K 线数据同步到 DuckDB 数据库。支持多种同步模式（初始化、日更新、周更新、月更新）
和自定义股票选择。
"""
from __future__ import annotations

import argparse
import json

from tqdm.auto import tqdm

from backend.app.core.config import get_settings
from backend.app.database import DuckDBDatabase
from backend.app.providers import HiThinkMarketDataProvider
from backend.app.repositories import MarketDataRepository
from backend.app.services import MarketDataService


def main() -> None:
    """主函数：解析命令行参数并执行数据同步。
    
    支持的命令行参数：
    - --mode: 同步模式（initial/daily/weekly/monthly），默认为 daily
    - --symbols: 要同步的股票代码（逗号分隔），默认全市场
    - --limit: 仅处理前 N 只股票，用于测试
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="同步 A 股一年期日 K 到 DuckDB")
    parser.add_argument("--mode", choices=["initial", "daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--symbols", help="逗号分隔的 thscode 或 6 位代码；默认全市场")
    parser.add_argument("--limit", type=int, help="仅处理前 N 只，适合试跑")
    args = parser.parse_args()

    # 加载配置文件
    settings = get_settings()
    
    # 初始化数据库连接和仓储
    database = DuckDBDatabase(settings.database_path)
    database.initialize()
    
    # 创建市场数据服务（包含 HiThink 数据提供者）
    service = MarketDataService(
        MarketDataRepository(database),
        HiThinkMarketDataProvider(
            settings.hithink_finance_api_key,
            settings.hithink_finance_base_url,
            timeout=settings.hithink_timeout_seconds,
            request_interval=settings.hithink_request_interval,
        ),
        history_days=settings.history_days,
        workers=settings.sync_workers,
    )
    
    # 解析要同步的股票代码（若指定）
    symbols = [item.strip() for item in args.symbols.split(",")] if args.symbols else None
    print("正在读取同花顺 A 股证券目录……", flush=True)

    # 进度条相关的变量
    progress_bar: tqdm | None = None
    last_completed = 0

    def display_progress(progress: dict) -> None:
        """更新进度条显示。
        
        Args:
            progress: 包含以下键值的进度字典：
                - total: 总股票数
                - completed: 已完成数
                - succeeded: 成功同步数
                - failed: 失败数
                - rows_written: 写入的数据行数
                - symbol: 当前处理的股票代码
        """
        nonlocal progress_bar, last_completed
        
        # 首次调用时初始化进度条
        if progress_bar is None:
            progress_bar = tqdm(
                total=progress["total"],
                desc=f"{args.mode} 同步",
                unit="只",
                dynamic_ncols=True,
            )
        
        # 计算并更新进度
        increment = progress["completed"] - last_completed
        if increment > 0:
            progress_bar.update(increment)
            last_completed = progress["completed"]
        
        # 更新进度条的附加信息
        progress_bar.set_postfix(
            成功=progress["succeeded"],
            失败=progress["failed"],
            写入行=progress["rows_written"],
            当前=progress["symbol"] or "准备中",
            refresh=True,
        )

    # 执行数据同步，确保进度条正确关闭
    try:
        result = service.sync(
            args.mode,
            symbols=symbols,
            limit=args.limit,
            progress_callback=display_progress,
        )
    finally:
        # 同步完成后关闭进度条
        if progress_bar is not None:
            progress_bar.close()

    # 以 JSON 格式输出同步结果
    print("\n同步结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# 脚本入口点
if __name__ == "__main__":
    main()
