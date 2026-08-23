"""同花顺问财最小连通性测试。"""

from backend.simple.provider.iwencai_provider import IwencaiProvider

import pandas as pd


def main() -> None:
    provider = IwencaiProvider()

    data = provider.query(
        "当前个股热度前1000，返回原始字段",
        page_size=50,
    )

    frame = pd.DataFrame(data)

    hot_col = next(col for col in frame.columns if col.startswith("个股热度"))

    frame = frame.rename(
        columns={
            "股票代码": "symbol",
            "股票简称": "name",
            "最新价": "price",
            "最新涨跌幅": "change_pct",
            hot_col: "hot_rank",
        }
    )

    print(f"共返回 {len(frame)} 条结果，以下展示前 500 条：\n{frame.head(500)}")


if __name__ == "__main__":
    main()
