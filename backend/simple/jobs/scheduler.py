from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.simple.config.config import Settings
from backend.simple.jobs.tasks import run_stock_hot_sync


def create_scheduler(settings: Settings) -> BackgroundScheduler:
    """创建 simple 应用的定时任务调度器。"""
    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)

    # 三个定时任务都会使用这些安全设置。
    common = {
        # 如果已经存在相同 id 的任务，就用新任务替换旧任务，避免重复登记。
        "replace_existing": True,
        # 同一个任务最多只允许一个实例运行，避免任务尚未结束又被再次启动。
        "max_instances": 1,
        # 如果程序暂停期间错过了多次执行，只在恢复后补执行一次。
        "coalesce": True,
    }
    scheduler.add_job(
        run_stock_hot_sync,
        CronTrigger(
            day_of_week="mon-fri",
            hour=18,
            minute=0,
            timezone=settings.scheduler_timezone,
        ),
        id="weekday-stock-hot-sync",
        **common,
    )
    return scheduler
