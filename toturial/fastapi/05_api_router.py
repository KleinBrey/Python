"""FastAPI 第 5 课：使用 APIRouter 组织接口。"""

from fastapi import APIRouter, FastAPI, Query


# 实际项目可把 router 放到 api/routes.py，把 app 放到 main.py。
market_router = APIRouter(prefix="/market", tags=["market"])
system_router = APIRouter(tags=["system"])


@system_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@market_router.get("/stocks")
def list_stocks(query: str | None = None, limit: int = Query(10, ge=1, le=100)) -> dict:
    return {"query": query, "limit": limit, "rows": []}


app = FastAPI(title="Router 示例")

# 项目的 /api 前缀统一在 include_router 时添加。
app.include_router(system_router, prefix="/api")
app.include_router(market_router, prefix="/api")


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    print(client.get("/api/health").json())
    print(client.get("/api/market/stocks", params={"query": "茅台"}).json())
    print("OpenAPI 中的路径：", sorted(app.openapi()["paths"]))
