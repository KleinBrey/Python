"""FastAPI 第 2 课：使用 Pydantic 约束接口响应。"""

from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel


class Bar(BaseModel):
    """一条日 K，与项目 daily_bars 的核心字段对应。"""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


class BarsResponse(BaseModel):
    """日 K 接口的完整响应。"""

    symbol: str
    rows: list[Bar]


app = FastAPI(title="响应模型示例")


@app.get("/api/market/bars/{symbol}", response_model=BarsResponse)
def get_bars(symbol: str) -> dict:
    return {
        "symbol": symbol,
        "rows": [
            {
                "date": "2026-08-20",  # Pydantic 会把字符串校验为日期
                "open": 11.20,
                "high": 11.40,
                "low": 11.19,
                "close": 11.40,
                "volume": 1_183_578.23,
                "internal_note": "不会出现在响应中",
            }
        ],
    }


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    response = TestClient(app).get("/api/market/bars/000001")
    print("状态码：", response.status_code)
    print("响应：", response.json())
    print("注意：response_model 已过滤 internal_note。")
