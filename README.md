# stock

一个面向 A 股数据的小项目，目前保留两条清晰入口：

1. `AkShare + MongoDB + React` 股票热度排行榜 Web 看板
2. `Tushare + MongoDB + Pandas + Pyecharts` 历史行情与量能策略流水线

## 项目结构

- [backend](/Users/kleinbrey/PycharmProjects/stock/backend)：Python HTTP API，当前主要服务 AkShare 热度榜单
- [frontend](/Users/kleinbrey/PycharmProjects/stock/frontend)：React + Vite + shadcn/ui + Tailwind CSS 前端页面
- [stock_core](/Users/kleinbrey/PycharmProjects/stock/stock_core)：Python 业务包
  - `data_sources`：外部数据源适配层，隔离 AkShare / Tushare SDK
  - `database`：MongoDB 简单封装和集合入口
  - `pipelines`：Tushare 股票池与历史行情缓存
  - `strategies`：策略筛选脚本及统一策略来源
    - `sources`：把问财结果和 Python 手写策略统一转换成股票列表
  - `charts`：Pyecharts K 线图生成
  - `utils`：通用工具函数
- [.vscode](/Users/kleinbrey/PycharmProjects/stock/.vscode)：VS Code 启动配置

前端核心目录：

- `src/config`：看板菜单、路由路径等配置
- `src/layouts`：shadcn/ui 应用布局
- `src/components/ui`：项目内维护的 shadcn/ui 组件源码
- `src/lib/utils.js`：shadcn/ui className 合并工具
- `src/routes`：浏览器路由分配
- `src/pages`：各个看板页面
- `src/components`：跨页面复用组件
- `src/hooks`：页面状态和数据加载逻辑
- `src/api`：后端 API 请求封装

## 环境

- Python 3.13
- Node.js 22+
- 本地 MongoDB：`mongodb://localhost:27017/`

安装 Python 依赖：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

安装前端依赖：

```bash
cd frontend
npm install
```

## MongoDB 集合

默认数据库：`python`

- `stock_hot_rankings`：AkShare 多平台股票热度榜单缓存
- `stock_pool`：过滤后的股票池
- `stock_history_data`：历史行情
- `stock_filter_result`：策略筛选结果

## 股票热度看板

当前覆盖的 AkShare 榜单：

- 雪球关注榜、雪球本周新增关注、雪球讨论榜、雪球交易分享榜
- 东方财富人气榜、东方财富飙升榜、东方财富港股人气榜
- 百度股市通 A 股、港股、美股热搜股票

启动 API：

```bash
PYTHONPATH=$(pwd) .venv/bin/python backend/server.py
```

默认地址：

```text
http://127.0.0.1:8001
```

启动前端：

```bash
cd frontend
npm run dev
```

浏览器会自动打开前端页面。如果没有自动打开，看终端里 Vite 输出的 `Local` 地址，例如：

```text
http://127.0.0.1:5173/
```

在 VS Code 里运行时，使用任务：

- `启动：完整看板`：同时启动后端 API 和前端页面
- `启动：前端页面`：只启动 React 页面
- `启动：后端 API`：只启动 Python API

前端看板使用浏览器路由：

- `/hot-rankings`：股票热度
- `/market-overview`：市场概览
- `/strategy-signals`：策略来源和统一股票列表
- `/iwencai-selector`：自然语言问财选股和动态结果表格
- `/data-sources`：数据源状态
- `/database`：MongoDB 状态

页面默认读取 MongoDB 缓存；点击“刷新全部”或单个榜单的“刷新”按钮时才会调用 AkShare 外部接口并更新缓存。

热榜注册表集中在 [stock_core/data_sources/hot_rankings.py](/Users/kleinbrey/PycharmProjects/stock/stock_core/data_sources/hot_rankings.py)。后端不会直接调用具体数据源 SDK。

当前热榜数据源：

- [stock_core/data_sources/akshare_provider.py](/Users/kleinbrey/PycharmProjects/stock/stock_core/data_sources/akshare_provider.py)：雪球、百度股市通等 AkShare 接口
- [stock_core/data_sources/eastmoney_provider.py](/Users/kleinbrey/PycharmProjects/stock/stock_core/data_sources/eastmoney_provider.py)：自写东方财富热榜数据源

单独查看东方财富热榜：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.data_sources.debug_eastmoney --limit 20
```

主要 API：

- `GET /api/health`
- `GET /api/summary`
- `GET /api/hot-rankings?limit=80&refresh=false`
- `GET /api/hot-rankings/{榜单ID}?limit=120&refresh=true`
- `GET /api/strategy-sources`
- `GET /api/strategy-stocks?source=all&limit=300`
- `GET /api/iwencai/status`
- `GET /api/iwencai/latest`
- `POST /api/iwencai/query`
- `GET /api/stocks/history?symbol=000938&period=daily`：通过 `hithink-market-query` 获取不复权历史行情

## 问财选股页面

“问财选股”页面允许直接输入自然语言条件。查询由本机后端调用同花顺问财 OpenAPI，API Key 不会发送到浏览器。后端会自动获取全部分页，并继续写入原问财项目：

- `~/Documents/问财选股/query.txt`
- `~/Documents/问财选股/results/latest.json`
- `~/Documents/问财选股/results/latest.csv`
- `~/Documents/问财选股/results/history/`

后端从环境变量或 `~/.zshrc`、`~/.zprofile`、`~/.profile` 读取：

```bash
export IWENCAI_API_KEY=your_api_key
export IWENCAI_BASE_URL=https://openapi.iwencai.com
```

配置更新后需要重启后端 API。

问财选股结果右侧的个股 K 线也使用同花顺问财行情技能。接口返回每日开高低收和成交量，周线、月线由后端基于日线聚合；当前明确标注为不复权数据。

## 策略来源

策略来源统一放在 [stock_core/strategies/sources](/Users/kleinbrey/PycharmProjects/stock/stock_core/strategies/sources)，最终都输出相同结构的股票列表。

当前来源：

- `iwencai`：默认读取 `~/Documents/问财选股/results/latest.json`
- `handwritten`：读取项目内注册的 Python 手写策略，当前已注册量能放大策略结果

问财目录可以通过环境变量覆盖：

```bash
export IWENCAI_PROJECT_DIR=/你的路径/问财选股
```

也可以直接指定结果文件：

```bash
export IWENCAI_RESULT_FILE=/你的路径/latest.json
```

新增手写策略时，在 `stock_core/strategies/sources/handwritten.py` 中注册一个返回字典列表的函数：

```python
@register_handwritten_strategy("my-strategy", "我的策略")
def load_my_strategy():
    return [{"股票代码": "000001", "股票名称": "平安银行"}]
```

## Tushare 流水线

Tushare 相关脚本只从环境变量读取 token：

```bash
export TUSHARE_TOKEN=your_token
```

生成股票池并拉取最近约 60 天历史行情：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.pipelines.run_all
```

运行量能放大策略：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.strategies.stock_volume_spike
```

生成 K 线图：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.charts.pyecharts_chart
```

输出文件：

- [output-chart/stock_result.html](/Users/kleinbrey/PycharmProjects/stock/output-chart/stock_result.html)

Tushare 调用集中在 [stock_core/data_sources/tushare_provider.py](/Users/kleinbrey/PycharmProjects/stock/stock_core/data_sources/tushare_provider.py)。股票池和历史行情脚本只依赖这里暴露的方法。

## 推荐使用顺序

看股票热度：

1. 启动 MongoDB
2. 启动 [backend/server.py](/Users/kleinbrey/PycharmProjects/stock/backend/server.py)
3. 启动 [frontend](/Users/kleinbrey/PycharmProjects/stock/frontend)
4. 在页面点击刷新榜单

跑历史行情策略：

1. 设置 `TUSHARE_TOKEN`
2. 跑 `python -m stock_core.pipelines.run_all`
3. 跑 `python -m stock_core.strategies.stock_volume_spike`
4. 跑 `python -m stock_core.charts.pyecharts_chart`

## 说明

- Web 看板不依赖 Tushare token
- Tushare 流水线依赖 MongoDB 中间结果串联后续步骤
- 图表输出、前端构建产物、依赖目录和 IDE 私有配置已加入忽略规则
