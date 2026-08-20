"""AkShare 行情最小连通性测试。"""

import pandas as pd

from backend.simple.provider.akshare_provider import AkShareProvider


def main() -> None:
    provider = AkShareProvider()

    data = provider.fetch_stock_list()["data"]["item"]

    frame = pd.DataFrame(data)

    print(f"共返回 {len(frame)} 条结果，以下展示前 20 条：\n{frame.head(20)}")


if __name__ == "__main__":
    main()
