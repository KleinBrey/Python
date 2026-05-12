# stock

一个基于 `Tushare + MongoDB + Pandas + Pyecharts` 的 A 股数据分析小项目。

它的主流程是：

1. 从 Tushare 拉取基础股票池
2. 按规则过滤股票池
3. 拉取股票历史行情并写入 MongoDB
4. 运行策略筛选目标股票
5. 生成 K 线图 HTML 页面

## 项目结构

- [data_source](/Users/kleinbrey/PycharmProjects/stock/data_source)：数据源脚本，主要是 Tushare / AkShare
- [mongodb](/Users/kleinbrey/PycharmProjects/stock/mongodb)：MongoDB 简单封装
- [stock_cache](/Users/kleinbrey/PycharmProjects/stock/stock_cache)：股票池和历史行情缓存流程
- [strategy](/Users/kleinbrey/PycharmProjects/stock/strategy)：策略筛选脚本
- [chart](/Users/kleinbrey/PycharmProjects/stock/chart)：图表生成脚本
- [.vscode](/Users/kleinbrey/PycharmProjects/stock/.vscode)：VS Code 启动配置

## 环境要求

- Python 3.13
- 本地 MongoDB，默认地址：`mongodb://localhost:27017/`
- 已安装项目依赖，当前项目使用本地虚拟环境 `.venv`

项目中实际会用到的核心依赖包括：

- `tushare`
- `pymongo`
- `pandas`
- `tqdm`
- `pyecharts`
- `mplfinance`
- `akshare`

## MongoDB 约定

默认使用数据库 `python`，主要集合如下：

- `stock_pool`：过滤后的股票池
- `stock_history_data`：历史行情
- `stock_filter_result`：策略筛选结果
- `stock_hot`：同花顺热股
- `stock_hot_dc`：东财热股

## Tushare Token

项目在 [data_source/__init__.py](/Users/kleinbrey/PycharmProjects/stock/data_source/__init__.py) 中初始化 Tushare。

优先读取环境变量：

```bash
export TUSHARE_TOKEN=your_token
```

如果没有设置环境变量，会回退到文件中的默认 token。

## 运行主流程

先确认 MongoDB 已启动，然后在项目根目录执行：

```bash
PYTHONPATH=$(pwd) .venv/bin/python stock_cache/run_all.py
```

这一步会完成：

1. 生成股票池
2. 拉取最近约 60 天的历史行情

## 运行策略

执行量能放大策略：

```bash
PYTHONPATH=$(pwd) .venv/bin/python strategy/stock_volume_spike.py
```

结果会写入 `stock_filter_result` 集合。

## 生成图表

执行：

```bash
PYTHONPATH=$(pwd) .venv/bin/python chart/pyecharts-chart.py
```

输出文件：

- [chart/output-chart/stock_result.html](/Users/kleinbrey/PycharmProjects/stock/chart/output-chart/stock_result.html)

## 热股脚本

抓取东财热股：

```bash
PYTHONPATH=$(pwd) .venv/bin/python stock_cache/stock_hot_dc.py
```

合并并查看热股结果：

```bash
PYTHONPATH=$(pwd) .venv/bin/python strategy/stock_hot.py
```

## VS Code 使用方式

项目已经补好了 VS Code 配置，打开仓库后可直接使用：

- `调试：当前脚本`
- `调试：当前脚本（项目根）`
- `运行：当前脚本`
- `运行：当前脚本（项目根）`

如果脚本依赖“脚本所在目录”作为工作目录，优先使用：

- `调试：当前脚本`
- `运行：当前脚本`

## 当前推荐顺序

如果你只是想从头跑一遍项目，建议按这个顺序：

1. 启动本地 MongoDB
2. 跑 [stock_cache/run_all.py](/Users/kleinbrey/PycharmProjects/stock/stock_cache/run_all.py)
3. 跑 [strategy/stock_volume_spike.py](/Users/kleinbrey/PycharmProjects/stock/strategy/stock_volume_spike.py)
4. 跑 [chart/pyecharts-chart.py](/Users/kleinbrey/PycharmProjects/stock/chart/pyecharts-chart.py)

## 说明

- 项目当前更偏“脚本式数据流水线”，不是 Web 服务
- 运行后会依赖 MongoDB 中间结果串联后续步骤
- 图表文件属于生成产物，已经加入忽略规则，不建议手动提交
