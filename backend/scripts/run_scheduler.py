from __future__ import annotations

from threading import Event

from backend.app.config.config import get_settings
from backend.app.jobs import create_scheduler


def main() -> None:
    settings = get_settings()
    scheduler = create_scheduler(settings)
    scheduler.start()
    print("调度器已启动；Ctrl+C 停止")
    try:
        Event().wait()
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
