# stock

一个面向 A 股数据的小项目，目前保留两条清晰入口：

1. `AkShare + MongoDB + React` 股票热度排行榜 Web 看板
2. `Tushare + MongoDB + Pandas + Pyecharts` 历史行情与量能策略流水线

## 项目结构

- [backend](/Users/kleinbrey/PycharmProjects/stock/backend)：Python HTTP API，当前主要服务 AkShare 热度榜单
- [frontend](/Users/kleinbrey/PycharmProjects/stock/frontend)：React + Vite 前端页面
- [stock_app](/Users/kleinbrey/PycharmProjects/stock/stock_app)：Python 业务包
  - `data_sources`：外部数据源适配层，隔离 AkShare / Tushare SDK
  - `database`：MongoDB 简单封装和集合入口
  - `pipelines`：Tushare 股票池与历史行情缓存
  - `strategies`：策略筛选脚本
  - `charts`：Pyecharts K 线图生成
  - `utils`：通用工具函数
- [.vscode](/Users/kleinbrey/PycharmProjects/stock/.vscode)：VS Code 启动配置

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

浏览器打开：

```text
http://127.0.0.1:5173/
```

页面默认读取 MongoDB 缓存；点击“刷新全部”或单个榜单的“刷新”按钮时才会调用 AkShare 外部接口并更新缓存。

热榜数据源集中在 [stock_app/data_sources/akshare_provider.py](/Users/kleinbrey/PycharmProjects/stock/stock_app/data_sources/akshare_provider.py)。后端不会直接调用 `akshare`，后续如果要替换成别的数据源，优先改这个适配文件。

主要 API：

- `GET /api/health`
- `GET /api/summary`
- `GET /api/hot-rankings?limit=80&refresh=false`
- `GET /api/hot-rankings/{榜单ID}?limit=120&refresh=true`

## Tushare 流水线

Tushare 相关脚本只从环境变量读取 token：

```bash
export TUSHARE_TOKEN=your_token
```

生成股票池并拉取最近约 60 天历史行情：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_app.pipelines.run_all
```

运行量能放大策略：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_app.strategies.stock_volume_spike
```

生成 K 线图：

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_app.charts.pyecharts_chart
```

输出文件：

- [output-chart/stock_result.html](/Users/kleinbrey/PycharmProjects/stock/output-chart/stock_result.html)

Tushare 调用集中在 [stock_app/data_sources/tushare_provider.py](/Users/kleinbrey/PycharmProjects/stock/stock_app/data_sources/tushare_provider.py)。股票池和历史行情脚本只依赖这里暴露的方法。

## 推荐使用顺序

看股票热度：

1. 启动 MongoDB
2. 启动 [backend/server.py](/Users/kleinbrey/PycharmProjects/stock/backend/server.py)
3. 启动 [frontend](/Users/kleinbrey/PycharmProjects/stock/frontend)
4. 在页面点击刷新榜单

跑历史行情策略：

1. 设置 `TUSHARE_TOKEN`
2. 跑 `python -m stock_app.pipelines.run_all`
3. 跑 `python -m stock_app.strategies.stock_volume_spike`
4. 跑 `python -m stock_app.charts.pyecharts_chart`

## 说明

- Web 看板不依赖 Tushare token
- Tushare 流水线依赖 MongoDB 中间结果串联后续步骤
- 图表输出、前端构建产物、依赖目录和 IDE 私有配置已加入忽略规则
