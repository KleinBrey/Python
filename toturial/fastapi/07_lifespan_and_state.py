"""FastAPI 第 7 课：用 lifespan 初始化和清理应用资源。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request


class StockRepository:
    def __init__(self) -> None:
        self.ready = True

    def count_stocks(self) -> int:
        return 5549

    def close(self) -> None:
        self.ready = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """yield 之前初始化，yield 之后清理。"""

    repository = StockRepository()
    app.state.repository = repository
    print("应用启动：Repository 已准备")
    try:
        yield
    finally:
        repository.close()
        print("应用关闭：Repository 已清理")


app = FastAPI(title="生命周期示例", lifespan=lifespan)


def get_repository(request: Request) -> StockRepository:
    return request.app.state.repository


Repository = Annotated[StockRepository, Depends(get_repository)]


@app.get("/api/market/status")
def market_status(repository: Repository) -> dict:
    return {
        "repository_ready": repository.ready,
        "stock_count": repository.count_stocks(),
    }


if __name__ == "__main__":
    # 使用 with 才会触发 TestClient 对应用 lifespan 的启动和关闭。
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        print("接口响应：", client.get("/api/market/status").json())

# 项目在 lifespan 中初始化 DuckDB、Repository、Provider、Service 和 Scheduler。
