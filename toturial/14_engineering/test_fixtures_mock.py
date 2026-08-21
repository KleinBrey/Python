"""
==================================================
知识点：pytest fixture 与 mock 基础
==================================================

运行：python -m pytest study/14_engineering/test_fixtures_mock.py -v
"""

try:
    import pytest
except ImportError:
    pytest = None


class PriceClient:
    def fetch(self, symbol: str) -> float:
        raise RuntimeError("真实客户端会访问网络，单元测试不应调用它")


def price_with_tax(client: PriceClient, symbol: str) -> float:
    return client.fetch(symbol) * 1.001


if pytest is not None:
    @pytest.fixture
    def fake_client():
        """fixture 提供可复用测试数据/对象，并可在 yield 后清理资源。"""
        class FakeClient:
            def fetch(self, symbol: str) -> float:
                return 100.0
        return FakeClient()


    def test_price_with_fixture(fake_client) -> None:
        assert price_with_tax(fake_client, "600519") == pytest.approx(100.1)


    def test_price_with_mock() -> None:
        # mock 替身记录调用并返回可控结果，避免测试依赖真实网络、时间或数据库。
        from unittest.mock import Mock
        client = Mock(spec=PriceClient)
        client.fetch.return_value = 200.0
        assert price_with_tax(client, "600519") == pytest.approx(200.2)
        client.fetch.assert_called_once_with("600519")


if __name__ == "__main__":
    if pytest is None:
        print("缺少 pytest，请运行：python -m pip install pytest")
    else:
        from unittest.mock import Mock
        client = Mock(spec=PriceClient)
        client.fetch.return_value = 100.0
        assert price_with_tax(client, "600519") == pytest.approx(100.1)
        print("mock 自检通过；fixture 测试请用 pytest 运行")

"""
本节总结：fixture 管理测试依赖；mock 隔离外部系统；不要 mock 自己真正想验证的逻辑。
"""
