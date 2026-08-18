"""
Tushare 中转/官方接口的最小连通性测试。
"""

from backend.simple.provider.tushare_provider import TushareProvider


def main() -> None:
    provider = TushareProvider()

    # 提取单个股票，跨时间段的历史日线
    df = provider.pro_api.daily(
        ts_code="000001.SZ", start_date="20180701", end_date="20200718"
    )
    print(df)


if __name__ == "__main__":
    main()
