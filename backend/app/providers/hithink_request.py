import requests

base_url: str = "https://fuyao.aicubes.cn"

HITHINK_FINANCE_API_KEY="sk-fuyao-ubQXGmGz8oPFVwDZ1wITPlbyTtPJwErA"


session = requests.Session()


session.headers.update({
    'X-api-key': HITHINK_FINANCE_API_KEY,
    'timeout':'20'
})



def fetch_data(url: str) -> dict:
    query_url = f"{base_url}{url}"
    try:
        response = session.get(query_url,params={"thscode": "300654"})
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
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
        print("数据获取成功")
    finally:
        print("请求流程结束")


result = fetch_data("/api/a-share/prices/snapshot")  # 替换为实际的 API 路径

print(result)  # 打印获取到的数据