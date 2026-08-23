from apscheduler.triggers.cron import CronTrigger

from backend.app.config.config import Settings
from backend.app.jobs import tasks
from backend.app.jobs import create_scheduler
from backend.app.jobs.tasks import run_daily_k_sync, run_stock_hot_sync


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


def test_daily_k_sync_schedules():
    scheduler = create_scheduler(
        Settings(
            scheduler_timezone="Asia/Shanghai",
            daily_update_hour=18,
            daily_update_minute=0,
        )
    )
    expected_jobs = {
        "weekday-daily-k-sync": (
            "cron[day_of_week='mon-fri', hour='18', minute='0']",
            (3, 100),
        ),
        "weekly-daily-k-calibration": (
            "cron[day_of_week='sat', hour='9', minute='0']",
            (60, 50),
        ),
        "monthly-daily-k-calibration": (
            "cron[day='1', hour='10', minute='0']",
            (365, 10),
        ),
    }

    for job_id, (trigger, args) in expected_jobs.items():
        job = scheduler.get_job(job_id)
        assert job is not None
        assert job.func is run_daily_k_sync
        assert str(job.trigger) == trigger
        assert str(job.trigger.timezone) == "Asia/Shanghai"
        assert job.args == args
        assert job.max_instances == 1
        assert job.coalesce is True


def test_daily_k_job_calls_sync_script(monkeypatch):
    calls = []
    monkeypatch.setattr(
        tasks,
        "sync_daily_k",
        lambda lookback_days, batch_size: calls.append(
            (lookback_days, batch_size)
        ),
    )

    run_daily_k_sync(60, 50)

    assert calls == [(60, 50)]
