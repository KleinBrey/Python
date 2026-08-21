"""FastAPI 第 3 课：校验 POST 请求体。"""

from typing import Literal

from fastapi import FastAPI, status
from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    """同步任务请求，字段贴合项目现有的四种同步模式。"""

    mode: Literal["initial", "daily", "weekly", "monthly"] = "daily"
    symbols: list[str] = Field(default_factory=list, max_length=20)


class SyncAccepted(BaseModel):
    status: str
    mode: str
    symbol_count: int


app = FastAPI(title="请求体示例")


@app.post(
    "/api/jobs/run",
    response_model=SyncAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
def run_job(request: SyncRequest) -> dict:
    return {
        "status": "accepted",
        "mode": request.mode,
        "symbol_count": len(request.symbols),
    }


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    accepted = client.post(
        "/api/jobs/run",
        json={"mode": "daily", "symbols": ["000001", "600519"]},
    )
    print("正确请求：", accepted.status_code, accepted.json())

    rejected = client.post("/api/jobs/run", json={"mode": "sometimes"})
    print("错误模式：", rejected.status_code)
    print("错误位置：", rejected.json()["detail"][0]["loc"])

# GET 通常用于读取；POST 通常用于提交数据或触发动作。
