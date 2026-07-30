# stock

面向 A 股的量化研究与看板项目。系统的结构化证券数据已经统一为
[同花顺扶摇 Financial API](https://fuyao.aicubes.cn/docs/)；问财 OpenAPI
只保留为自然语言选股入口，选中股票后的代码解析和 K 线仍由扶摇 API 提供。

## 数据架构

```text
同花顺扶摇 REST API ─┐
                     ├─ data/providers ─ data/service ─ 策略 / MongoDB / 后端 API
问财自然语言选股 ────┘
```

- [data](/Users/kleinbrey/PycharmProjects/stock/data)：独立统一数据层
  - `providers/hithink_financial.py`：代码表、行情快照、日 K、估值、热榜的官方适配器
  - `providers/iwencai_api.py`：自然语言选股，不提供行情
  - `service.py`：业务层唯一结构化取数门面
  - `normalizers.py` / `schemas.py`：供应商字段转换、清洗和系统稳定契约
  - `raw` / `processed` / `cache` / `exports`：运行时数据
- [backend](/Users/kleinbrey/PycharmProjects/stock/backend)：Python HTTP API
- [frontend](/Users/kleinbrey/PycharmProjects/stock/frontend)：React + Vite 看板
- [stock_core](/Users/kleinbrey/PycharmProjects/stock/stock_core)：MongoDB、流水线和策略

策略和业务代码不得直接依赖供应商字段。今后若更换或增加供应商，只在 `data/`
内增加适配器并转换成系统契约。

## 配置

Python 3.13、Node.js 22+，本地 MongoDB 默认地址为
`mongodb://localhost:27017/`。

```bash
.venv/bin/python -m pip install -e .
cd frontend && npm install
```

Python 项目元数据和依赖统一维护在
[pyproject.toml](/Users/kleinbrey/PycharmProjects/stock/pyproject.toml)。
安装后也可以直接使用 `stock-api` 和 `stock-pipeline` 命令。

项目内的私密配置保存在 `config/secrets.local.toml`。该文件已加入
`.gitignore`，不会随代码提交；可提交的字段模板是
`config/secrets.example.toml`。

```bash
cp config/secrets.example.toml config/secrets.local.toml
```

然后只在 `config/secrets.local.toml` 中填写 `HITHINK_FINANCE_API_KEY` 和
`IWENCAI_API_KEY`。项目本地配置优先于环境变量，不需要再向系统环境导出 API Key。

查看不经过项目封装的原始 REST 调用案例：

```bash
bash examples/fuyao_curl_examples.sh snapshot 600519.SH
bash examples/fuyao_curl_examples.sh history 000001.SZ 60
```

curl 案例：[examples/fuyao_curl_examples.sh](/Users/kleinbrey/PycharmProjects/stock/examples/fuyao_curl_examples.sh)

Python 案例：[examples/fuyao_api_example.py](/Users/kleinbrey/PycharmProjects/stock/examples/fuyao_api_example.py)

环境变量和 `~/.zshrc`、`~/.zprofile`、`~/.profile` 仅作为旧配置兼容回退。
修改本地配置后需重启后端。

## 启动

```bash
PYTHONPATH=$(pwd) .venv/bin/python backend/server.py
cd frontend && npm run dev
```

默认后端地址为 `http://127.0.0.1:8001`，前端通常为
`http://127.0.0.1:5173/`。

主要页面：

- `/hot-rankings`：同花顺 24 小时/小时热股榜、飙升榜和涨停池
- `/market-overview`：市场概览
- `/strategy-signals`：统一策略来源
- `/iwencai-selector`：问财自然语言选股
- `/data-sources`：扶摇 API 配置与连通状态
- `/database`：MongoDB 集合状态

个股 K 线由 `GET /api/stocks/history` 从扶摇历史行情接口获取，前端使用
TradingView Lightweight Charts 显示；支持日线，以及由后端从日线聚合的周线和月线，
支持不复权、前复权和后复权。问财筛选完成后，前端会调用
`POST /api/stocks/history/prefetch`，以有限并发预缓存筛选结果的日线；随后点击股票或
切换日/周/月周期都会复用缓存。

## 流水线

```bash
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.pipelines.run_all
PYTHONPATH=$(pwd) .venv/bin/python -m stock_core.strategies.stock_volume_spike
```

流水线的股票代码表、估值和历史行情全部走扶摇 API。历史接口一次只接受一个
`thscode`，统一 service 会将批量股票拆成多个官方请求再合并为相同格式。

扶摇当前文档将“股票基础信息”标为规划中，代码表尚不提供行业、上市状态、总股本和
总市值。因此这些统一字段会保留为空，股票池会明确提示并跳过原有的市值过滤，
不会用其他来源补齐或构造虚假值。官方接口上线这些字段后，只需在
`data/providers/hithink_financial.py` 补映射。

## API

- `GET /api/health`
- `GET /api/summary`
- `GET /api/data-sources?check=true`
- `GET /api/hot-rankings?limit=80&refresh=true`
- `GET /api/hot-rankings/{榜单ID}?refresh=true`
- `GET /api/stocks/history?symbol=000938&period=daily&adjust=qfq`
- `GET /api/strategy-sources`
- `GET /api/strategy-stocks?source=all&limit=300`
- `GET /api/iwencai/status`
- `GET /api/iwencai/latest`
- `POST /api/iwencai/query`

## 运行时数据

默认数据根目录就是项目的 `data/`。可整体迁移到其他磁盘：

```bash
export STOCK_DATA_DIR=/你的数据磁盘/stock-data
```

问财结果默认写入：

```text
data/raw/iwencai/query.txt
data/raw/iwencai/results/latest.json
data/raw/iwencai/results/latest.csv
data/raw/iwencai/results/history/
```

可用 `IWENCAI_PROJECT_DIR`、`IWENCAI_OUTPUT_DIR` 或
`IWENCAI_RESULT_FILE` 覆盖对应路径。
