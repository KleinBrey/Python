import logging

from backend.app.scripts.sync_daily_k_db import sync_daily_k
from backend.app.scripts.sync_stock_hot_db import main as sync_stock_hot
from backend.app.scripts.sync_stock_list_db import main as sync_stock_list

logger = logging.getLogger(__name__)


def run_stock_list_sync() -> None:
    """执行股票列表同步脚本，并记录未处理的同步异常。"""
    try:
        sync_stock_list()
        logger.info("股票列表同步完成")
    except Exception:
        logger.exception("股票列表同步失败")


def run_stock_hot_sync() -> None:
    """执行热门股同步脚本，并记录未处理的同步异常。"""
    try:
        sync_stock_hot()
        logger.info("热门股同步完成")
    except Exception:
        logger.exception("热门股同步失败")


def run_daily_k_sync(lookback_days: int, batch_size: int) -> None:
    """执行指定回看范围的日 K 同步，并记录未处理的同步异常。"""
    try:
        sync_daily_k(lookback_days, batch_size)
        logger.info("日 K 同步完成: lookback_days=%s", lookback_days)
    except Exception:
        logger.exception("日 K 同步失败: lookback_days=%s", lookback_days)
