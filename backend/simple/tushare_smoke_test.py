"""Tushare 中转/官方接口的最小连通性测试。

先在 ``backend/.env`` 中配置 ``TUSHARE_TOKEN``。默认走中转；若要测试官方
接口，再配置 ``TUSHARE_USE_RELAY=false``。

运行：
    .venv/bin/python -m backend.simple.tushare_smoke_test
"""

from backend.simple.provider.tushare_provider import TushareProvider


def main() -> None:
    provider = TushareProvider()
    frame = provider.pro_api.daily(ts_code="000001.SZ", limit=3)
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
