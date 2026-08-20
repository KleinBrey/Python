"""同花顺问财最小连通性测试。"""

from pprint import pprint

from backend.simple.provider.iwencai_provider import IwencaiProvider

import pandas as pd


def main() -> None:
    provider = IwencaiProvider()

    data = provider.query(
        "当前个股热度前500，返回原始字段",
        page_size=50,
    )

    print(f"共返回 {len(data)} 条结果，以下展示前 50 条：")
    pprint(pd.DataFrame(data[:50]))


if __name__ == "__main__":
    main()
