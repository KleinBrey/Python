import logging

from backend.app.services import MarketDataService, SyncAlreadyRunningError


logger = logging.getLogger(__name__)


def run_sync(service: MarketDataService, mode: str) -> None:
    try:
        logger.info("行情同步完成: %s", service.sync(mode))
    except SyncAlreadyRunningError:
        logger.warning("跳过 %s：已有同步任务运行中", mode)
    except Exception:
        logger.exception("行情同步失败: mode=%s", mode)

