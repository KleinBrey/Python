"""FastAPI 第 8 课：接受任务后在后台执行。"""

from typing import Literal

from fastapi import BackgroundTasks, FastAPI, status


app = FastAPI(title="后台任务示例")
completed_jobs: list[str] = []


def sync_market_data(mode: str) -> None:
    """真实项目中，这里会调用 MarketDataService.sync。"""

    completed_jobs.append(mode)


@app.post("/api/jobs/run", status_code=status.HTTP_202_ACCEPTED)
def trigger_sync(
    background_tasks: BackgroundTasks,
    mode: Literal["initial", "daily", "weekly", "monthly"] = "daily",
) -> dict[str, str]:
    background_tasks.add_task(sync_market_data, mode)
    return {"status": "accepted", "mode": mode}


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.post("/api/jobs/run", params={"mode": "weekly"})
    print("接口立即返回：", response.status_code, response.json())
    print("测试客户端等待后台任务完成：", completed_jobs)

# 202 表示“已接受”，不代表任务一定成功。生产项目还应保存任务状态和错误信息。
