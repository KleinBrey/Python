import requests

import time

import pandas as pd

from pprint import pprint

BASE_URL: str = "https://fuyao.aicubes.cn"

HITHINK_FINANCE_API_KEY: str = "sk-fuyao-ubQXGmGz8oPFVwDZ1wITPlbyTtPJwErA"


session = requests.Session()


session.headers.update({"X-api-key": HITHINK_FINANCE_API_KEY})

"""
  同花顺接口统一调用方法
"""


def get(url: str, params: dict) -> dict:
    query_url = f"{BASE_URL}/{url}"
    try:
        response = session.get(query_url, params=params)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误：{http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"连接错误：{conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"请求超时：{timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求异常：{req_err}")
    except ValueError as json_err:
        print(f"JSON 解析错误：{json_err}")
    else:
        # try里的代码运行没有问题再走到这一步
        response.raise_for_status()
        print(f"接口响应成功，状态码：{response.status_code}")
        return response.json()


# 全市场股票列表获取
def fetch_stock_list() -> pd.DataFrame:
    url = "api/meta/tickers/list"
    # 初始化分页偏移量
    offset = 0
    # 定义每页返回的股票数量默认是1000
    limit = 10000
    params = {
        "asset_type": "a-share",  # 资产类型过滤：A 股
        "limit": limit,  # 每页数量
        "offset": offset,  # 分页偏移
    }
    result = get(url, params)
    return result


# 格式化股票列表数据
def format_stock_list(value: list) -> pd.DataFrame:
    frame = pd.DataFrame(value)
    columns = ["symbol", "name", "exchange", "type", "source"]
    # 如果 DataFrame 为空，返回只有列定义的空 DataFrame
    if frame.empty:
        return pd.DataFrame(columns=columns)
    # 格式转换
    frame["symbol"] = frame["ticker"]
    # 将提取的代码列添加到 DataFrame
    frame["type"] = frame["asset_type"]
    frame["source"] = "Hithink"

    # 只保留目标列，并按 columns 中的顺序排列
    return frame[columns].reset_index(drop=True)


# 获取当前股票快照
def fetch_snapshot(thscode: str, limit: int = 100, offset: int = 0) -> dict:
    url = "api/a-share/prices/snapshot"
    params = {"thscodes": thscode, limit: limit, offset: offset}
    result = get(url, params)
    return result


# 获取股票历史日线数据
def fetch_historical(
    thscode: str,
    start: int,
    end: int,
    interval: str = "1d",
    adjust: str = "forward",
    offset: int = 0,
) -> dict:
    url = "api/a-share/prices/historical"
    params = {
        "thscode": thscode,
        "interval": interval,
        "start": start,
        "end": end,
        "adjust": adjust,
        "offset": offset,
    }
    result = get(url, params)
    return result


snap_data = fetch_stock_list()

df = format_stock_list(snap_data["data"]["item"])

pprint(df)


# snap_data = fetch_snapshot("600519.SH")  # 调用函数获取数据

# pprint(snap_data)


# end = int(time.time() * 1000)

# start = end - 30 * 24 * 60 * 60 * 1000

# print(time.time(), start, end)

# history_data = fetch_historical("600519.SH", start, end)

# pprint(history_data)  # 打印获取到的数据
