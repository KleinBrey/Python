"""
==================================================
知识点：HTTP GET/POST、参数、响应与异常
==================================================

默认只运行离线演示；执行 python 00_http_requests.py --live 才请求网络。
先安装：python -m pip install requests
"""

import sys

def explain_offline() -> None:
    print("GET 通常读取资源；POST 通常提交或创建资源。")
    print("query params 位于 URL；headers 携带认证/格式等元数据；JSON body 是请求体。")
    print("2xx 通常成功，4xx 多为请求问题，5xx 多为服务器问题。")


def live_demo() -> None:
    try:
        import requests
    except ImportError:
        print("缺少 requests，请运行：python -m pip install requests")
        return

    url = "https://httpbin.org/get"
    try:
        response = requests.get(
            url,
            params={"symbol": "600519"},
            headers={"Accept": "application/json", "User-Agent": "python-study/1.0"},
            timeout=10,
        )
        # timeout 防止服务不响应时程序无限等待。生产环境可分别设置连接/读取超时。
        response.raise_for_status()  # 4xx/5xx 转为 HTTPError
        data = response.json()
        print("状态码：", response.status_code)
        print("服务器收到的参数：", data["args"])
    except requests.RequestException as error:
        print("HTTP 请求失败：", error)

    # POST JSON 示例（为避免重复网络请求，这里只展示写法）：
    # requests.post(url, json={"symbol": "600519"}, timeout=10)


if __name__ == "__main__":
    explain_offline()
    if "--live" in sys.argv:
        live_demo()

"""
本节总结：请求必须设 timeout；检查状态码；response.json() 解析 JSON；捕获请求异常。
"""
