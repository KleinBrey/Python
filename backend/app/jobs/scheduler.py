"""创建行情数据的定时任务调度器。

可以把调度器理解成一个“定时闹钟”：
应用启动时先在这里登记好任务，到了指定时间后，调度器会自动调用
``run_sync`` 执行行情数据同步。

本模块只负责“什么时候执行”和“用什么模式执行”。真正的数据同步逻辑
由 ``MarketDataService`` 完成。
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.core.config import Settings
from backend.app.jobs.tasks import run_sync
from backend.app.services import MarketDataService


def create_scheduler(
    settings: Settings, service: MarketDataService
) -> BackgroundScheduler:
    """创建并配置行情同步调度器。

    Args:
        settings: 应用配置，提供时区及每日任务的执行时间。
        service: 行情数据服务。定时任务触发后，使用它执行数据同步。

    Returns:
        已经添加好定时任务的调度器。

        注意：这里只创建调度器并添加任务，不会启动调度器。
        调度器会在应用启动阶段根据配置决定是否调用 ``start()``。
    """

    # BackgroundScheduler 在后台线程中运行，不会阻塞 FastAPI 继续处理请求。
    # timezone 用于解释下面所有任务的执行时间，例如 Asia/Shanghai 表示北京时间。
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
    # 下方的 **common 会把这个字典展开成 add_job 的三个关键字参数。

    # 每日更新：周一到周五，在配置指定的时间执行。
    # 例如 hour=18、minute=0 表示工作日每天 18:00 执行。
    scheduler.add_job(
        # 到达执行时间后，调度器会调用 run_sync。
        run_sync,
        # CronTrigger 用类似日历的规则描述任务应该在什么时候运行。
        CronTrigger(
            day_of_week="mon-fri",
            hour=settings.daily_update_hour,
            minute=settings.daily_update_minute,
            timezone=settings.scheduler_timezone,
        ),
        # id 是任务的唯一标识，也用于 replace_existing 判断是否为同一任务。
        id="daily-market-update",
        # 等价于到点后执行：run_sync(service, "daily")。
        args=[service, "daily"],
        **common,
    )

    # 每周校准：每周六 09:00 执行，重新检查最近 60 个交易日的数据。
    scheduler.add_job(
        run_sync,
        CronTrigger(
            day_of_week="sat",
            hour=9,
            minute=0,
            timezone=settings.scheduler_timezone,
        ),
        id="weekly-60-session-calibration",
        # 等价于到点后执行：run_sync(service, "weekly")。
        args=[service, "weekly"],
        **common,
    )

    # 每月校准：每月 1 日 10:00 执行，重新检查最近一年的数据。
    scheduler.add_job(
        run_sync,
        CronTrigger(
            day=1,
            hour=10,
            minute=0,
            timezone=settings.scheduler_timezone,
        ),
        id="monthly-one-year-calibration",
        # 等价于到点后执行：run_sync(service, "monthly")。
        args=[service, "monthly"],
        **common,
    )

    # 返回给应用启动代码。调用方负责启动和关闭这个调度器。
    return scheduler
