"""FastAPI 第 0 课：创建第一个股票 API。"""

from fastapi import FastAPI


# FastAPI 对象就是整个 Web 应用。
app = FastAPI(title="A 股行情学习 API", version="1.0.0")


@app.get("/")
def root() -> dict[str, str]:
    """访问根路径时返回一个普通字典，FastAPI 会自动转成 JSON。"""

    return {"name": "A 股行情学习 API", "docs": "/docs"}


@app.get("/api/health")
def health() -> dict[str, str]:
    """健康检查通常只确认服务能否正常响应。"""

    return {"status": "ok"}


if __name__ == "__main__":
    # TestClient 可以在不启动端口的情况下调用 API，适合学习和测试。
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/health")
    print("状态码：", response.status_code)
    print("响应 JSON：", response.json())

# 浏览器运行方式见 README。启动后 FastAPI 会自动提供 /docs 和 /redoc。
