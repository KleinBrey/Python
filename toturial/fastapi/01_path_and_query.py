"""FastAPI 第 1 课：路径参数和查询参数。"""

from datetime import date

from fastapi import FastAPI, Query


app = FastAPI(title="股票参数示例")


@app.get("/api/market/bars/{symbol}")
def get_bars(
    symbol: str,                         # 路径参数，例如 600519
    start_date: date | None = None,      # 可选查询参数，FastAPI 自动解析日期
    end_date: date | None = None,
    limit: int = Query(5, ge=1, le=20),  # 必须在 1～20 之间
) -> dict:
    return {
        "symbol": symbol.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit,
    }


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)

    response = client.get(
        "/api/market/bars/600519",
        params={"start_date": "2026-08-01", "limit": 3},
    )
    print("正确请求：", response.status_code, response.json())

    # limit 超过上限时，路由函数不会执行，FastAPI 直接返回 422。
    wrong = client.get("/api/market/bars/600519", params={"limit": 100})
    print("错误请求：", wrong.status_code)
    print("错误信息：", wrong.json()["detail"][0]["msg"])
