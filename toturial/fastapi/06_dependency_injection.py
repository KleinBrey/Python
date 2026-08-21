"""FastAPI 第 6 课：使用 Depends 注入 Repository。"""

from typing import Annotated

from fastapi import Depends, FastAPI, Query


class StockRepository:
    """Repository 负责提供数据；这里先使用内存数据代替 DuckDB。"""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows

    def search(self, query: str | None, limit: int) -> list[dict[str, str]]:
        result = self.rows
        if query:
            result = [
                row
                for row in result
                if query in row["symbol"] or query in row["name"]
            ]
        return result[:limit]


repository = StockRepository(
    [
        {"symbol": "000001", "name": "平安银行"},
        {"symbol": "600519", "name": "贵州茅台"},
    ]
)


def get_repository() -> StockRepository:
    """依赖函数决定路由实际使用哪个 Repository。"""

    return repository


Repository = Annotated[StockRepository, Depends(get_repository)]
app = FastAPI(title="依赖注入示例")


@app.get("/api/stocks")
def list_stocks(
    repository: Repository,
    query: str | None = None,
    limit: int = Query(10, ge=1, le=100),
) -> list[dict[str, str]]:
    return repository.search(query, limit)


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    print("真实依赖：", client.get("/api/stocks", params={"query": "茅台"}).json())

    # 测试时可替换依赖，不需要连接真实数据库或访问网络。
    fake = StockRepository([{"symbol": "TEST", "name": "测试股票"}])
    app.dependency_overrides[get_repository] = lambda: fake
    print("替换依赖：", client.get("/api/stocks").json())
    app.dependency_overrides.clear()

# 路由只关心 repository.search，不关心数据来自 DuckDB、接口还是测试假数据。
