import logging

from backend.simple.scripts.sync_stock_hot_db import main as sync_stock_hot

logger = logging.getLogger(__name__)


def run_stock_hot_sync() -> None:
    """执行热门股同步脚本，并记录未处理的同步异常。"""
    try:
        sync_stock_hot()
        logger.info("热门股同步完成")
    except Exception:
        logger.exception("热门股同步失败")
