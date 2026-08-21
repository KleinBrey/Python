"""FastAPI 第 9 课：使用 TestClient 和 pytest 测试接口。"""

from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException, Query
from fastapi.testclient import TestClient


app = FastAPI(title="接口测试示例")

STOCKS = [
    {"symbol": "000001", "name": "平安银行"},
    {"symbol": "600519", "name": "贵州茅台"},
]


@app.get("/api/stocks")
def list_stocks(limit: int = Query(10, ge=1, le=100)) -> list[dict[str, str]]:
    return STOCKS[:limit]


@app.get("/api/stocks/{symbol}")
def get_stock(symbol: str) -> dict[str, str]:
    for stock in STOCKS:
        if stock["symbol"] == symbol:
            return stock
    raise HTTPException(status_code=404, detail="股票不存在")


client = TestClient(app)


def test_list_stocks() -> None:
    response = client.get("/api/stocks", params={"limit": 1})

    assert response.status_code == 200
    assert response.json() == [{"symbol": "000001", "name": "平安银行"}]


def test_invalid_limit() -> None:
    response = client.get("/api/stocks", params={"limit": 0})

    assert response.status_code == 422


def test_stock_not_found() -> None:
    response = client.get("/api/stocks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "股票不存在"


if __name__ == "__main__":
    # 也可以运行：pytest toturial/fastapi/09_testing_with_testclient.py -q
    raise SystemExit(
        pytest.main([str(Path(__file__).resolve()), "-q", "-p", "no:cacheprovider"])
    )
