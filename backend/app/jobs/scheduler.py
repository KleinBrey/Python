from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.app.core.config import Settings
from backend.app.jobs.tasks import run_sync
from backend.app.services import MarketDataService


def create_scheduler(settings: Settings, service: MarketDataService) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
    common = {"replace_existing": True, "max_instances": 1, "coalesce": True}
    scheduler.add_job(
        run_sync,
        CronTrigger(
            day_of_week="mon-fri",
            hour=settings.daily_update_hour,
            minute=settings.daily_update_minute,
            timezone=settings.scheduler_timezone,
        ),
        id="daily-market-update",
        args=[service, "daily"],
        **common,
    )
    scheduler.add_job(
        run_sync,
        CronTrigger(day_of_week="sat", hour=9, minute=0, timezone=settings.scheduler_timezone),
        id="weekly-60-session-calibration",
        args=[service, "weekly"],
        **common,
    )
    scheduler.add_job(
        run_sync,
        CronTrigger(day=1, hour=10, minute=0, timezone=settings.scheduler_timezone),
        id="monthly-one-year-calibration",
        args=[service, "monthly"],
        **common,
    )
    return scheduler

