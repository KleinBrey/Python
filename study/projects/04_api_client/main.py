"""
==================================================
综合实战 4：可测试的 API 客户端
==================================================

默认使用离线 FakeSession；真实 HTTP 客户端应同样设置 timeout 并处理异常。
"""

from dataclasses import dataclass
from typing import Any, Protocol

class Response(Protocol):
    def raise_for_status(self) -> None: ...
    def json(self) -> dict[str, Any]: ...

class Session(Protocol):
    def get(self, url: str, *, params: dict[str, str], timeout: float) -> Response: ...

@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float

class ApiClient:
    def __init__(self, session: Session, base_url: str, timeout: float = 10.0):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_quote(self, symbol: str) -> Quote:
        response = self.session.get(
            f"{self.base_url}/quote", params={"symbol": symbol}, timeout=self.timeout
        )
        response.raise_for_status()
        payload = response.json()
        return Quote(symbol=str(payload["symbol"]), price=float(payload["price"]))

class FakeResponse:
    def raise_for_status(self) -> None:
        pass
    def json(self) -> dict[str, Any]:
        return {"symbol": "600519", "price": 1688.0}

class FakeSession:
    def get(self, url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        print("模拟请求：", url, params, f"timeout={timeout}")
        return FakeResponse()

def main() -> None:
    client = ApiClient(FakeSession(), "https://api.example.invalid")
    print(client.get_quote("600519"))

if __name__ == "__main__":
    main()
