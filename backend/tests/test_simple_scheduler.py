from apscheduler.triggers.cron import CronTrigger

from backend.simple.config.config import Settings
from backend.simple.jobs import tasks
from backend.simple.jobs import create_scheduler
from backend.simple.jobs.tasks import run_stock_hot_sync


def test_stock_hot_sync_runs_at_18_on_weekdays():
    scheduler = create_scheduler(Settings(scheduler_timezone="Asia/Shanghai"))

    job = scheduler.get_job("weekday-stock-hot-sync")

    assert job is not None
    assert job.func is run_stock_hot_sync
    assert isinstance(job.trigger, CronTrigger)
    assert str(job.trigger) == (
        "cron[day_of_week='mon-fri', hour='18', minute='0']"
    )
    assert str(job.trigger.timezone) == "Asia/Shanghai"
    assert job.max_instances == 1
    assert job.coalesce is True


def test_stock_hot_job_calls_sync_script(monkeypatch):
    calls = []
    monkeypatch.setattr(tasks, "sync_stock_hot", lambda: calls.append("called"))

    run_stock_hot_sync()

    assert calls == ["called"]
