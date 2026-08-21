"""FastAPI 第 4 课：股票代码标准化与 HTTP 错误。"""

from fastapi import FastAPI, HTTPException


app = FastAPI(title="错误处理示例")

LOCAL_BARS = {
    "000001.SZ": [{"date": "2026-08-20", "close": 11.40}],
    "600519.SH": [{"date": "2026-08-20", "close": 1291.50}],
}


def normalize_symbol(value: str) -> str:
    """把六位代码补成项目使用的完整 thscode。"""

    symbol = value.strip().upper()
    if "." in symbol:
        return symbol
    if len(symbol) != 6 or not symbol.isdigit():
        raise HTTPException(status_code=422, detail="股票代码应为 6 位数字")

    exchange = "SH" if symbol.startswith(("5", "6", "9")) else "SZ"
    return f"{symbol}.{exchange}"


@app.get("/api/market/bars/{symbol}")
def get_bars(symbol: str) -> dict:
    normalized = normalize_symbol(symbol)
    rows = LOCAL_BARS.get(normalized)
    if not rows:
        raise HTTPException(status_code=404, detail=f"没有 {normalized} 的日 K")
    return {"symbol": normalized, "rows": rows}


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    for path in ["600519", "123", "300750"]:
        response = client.get(f"/api/market/bars/{path}")
        print(path, "->", response.status_code, response.json())

# 422 表示输入格式不符合要求；404 表示格式正确，但目标数据不存在。
