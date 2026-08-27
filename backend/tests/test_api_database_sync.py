import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api import routes
from backend.app.api.routes import router


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.parametrize(
    ("path", "function_name", "expected_arguments", "expected_script"),
    [
        (
            "/database-sync/stock-list",
            "sync_stock_list",
            (),
            "sync_stock_list_db.py",
        ),
        (
            "/database-sync/daily-k",
            "sync_daily_k",
            (3, 100),
            "sync_daily_k_db.py",
        ),
        (
            "/database-sync/hot-stock",
            "sync_stock_hot",
            (),
            "sync_hot_stock_db.py",
        ),
    ],
)
def test_database_sync_endpoint_executes_mapped_script(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    function_name: str,
    expected_arguments: tuple,
    expected_script: str,
):
    calls = []

    def fake_sync(*args, **kwargs):
        calls.append(args or tuple(kwargs.values()))

    monkeypatch.setattr(routes, function_name, fake_sync)

    response = client.post(path)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["script"] == expected_script
    assert calls == [expected_arguments]


def test_database_sync_endpoint_returns_script_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def failed_sync():
        raise RuntimeError("上游接口不可用")

    monkeypatch.setattr(routes, "sync_stock_list", failed_sync)

    response = client.post("/database-sync/stock-list")

    assert response.status_code == 500
    assert response.json()["detail"] == "sync_stock_list_db.py 执行失败：上游接口不可用"
