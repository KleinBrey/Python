# 后端文件说明

本目录是本地 A 股行情系统的后端。技术栈为 FastAPI、DuckDB、Pandas 和 APScheduler，行情数据由同花顺 HiThink Financial API 提供。

## 调用关系

```text
FastAPI / 定时任务 / 命令行脚本
              │
              ▼
          services
       业务逻辑与数据清洗
         │           │
         ▼           ▼
    providers     repositories
    外部行情源      DuckDB 读写
                         │
                         ▼
                    market.duckdb
```

依赖方向应保持单向：API 和任务调用 service，service 调用 provider 与 repository。API、任务和业务代码不应直接编写 DuckDB SQL，也不应直接处理同花顺原始字段。

## 根目录文件

### `requirements.txt`

后端 Python 依赖清单，包括：

- `fastapi`：HTTP API 框架；
- `uvicorn`：ASGI 服务器；
- `duckdb`：本地分析型数据库；
- `pandas`：行情清洗和 DataFrame 转换；
- `requests`：调用同花顺 Financial API；
- `APScheduler`：每日更新及周期校准；
- `pydantic-settings`：读取 `.env` 配置；
- `pytest`、`httpx`：测试工具。

安装命令：

```bash
.venv/bin/python -m pip install -r backend/requirements.txt
```

### `.env`

本地真实运行配置，不提交 Git。主要配置包括：

- `HITHINK_FINANCE_API_KEY`：同花顺 Financial API Key；
- `HITHINK_FINANCE_BASE_URL`：同花顺 API 地址；
- `DATABASE_PATH`：DuckDB 文件路径；
- `SCHEDULER_ENABLED`：是否随 FastAPI 启动调度器；
- `SCHEDULER_TIMEZONE`：任务时区；
- `DAILY_UPDATE_HOUR`、`DAILY_UPDATE_MINUTE`：每日更新时间；
- `SYNC_WORKERS`：并发拉取股票数量；
- `HISTORY_DAYS`：初始化和月度校准的自然日跨度。

### `.env.example`

可提交的配置模板，只列出配置名称和示例值，不保存真实 API Key。

### `run.py`

后端快捷启动入口，使用 Uvicorn 在 `127.0.0.1:8001` 启动 FastAPI。

```bash
PYTHONPATH=. .venv/bin/python backend/run.py
```

## `app/`：后端应用

### `app/main.py`

FastAPI 应用入口，负责：

- 创建 FastAPI 实例；
- 初始化 DuckDB 表结构；
- 组装 provider、repository 和 service；
- 配置跨域访问；
- 注册 `/api` 路由；
- 根据配置启动和停止 APScheduler。

开发模式启动：

```bash
PYTHONPATH=. .venv/bin/uvicorn backend.app.main:app \
  --host 127.0.0.1 --port 8001 --reload
```

### `app/api/`

FastAPI 接口层。

- `routes.py`：定义健康检查、数据库状态、股票列表、日 K 查询和手动同步接口；
- `dependencies.py`：从 FastAPI `app.state` 中取得 repository 和 service；
- `__init__.py`：导出统一 API router。

当前接口：

- `GET /api/health`：服务健康检查；
- `GET /api/market/status`：数据库、数据覆盖和最近同步状态；
- `GET /api/stocks`：查询本地股票主数据；
- `GET /api/market/bars/{symbol}`：查询股票日 K；
- `POST /api/jobs/run?mode=daily`：提交后台同步任务。

API 层只负责参数校验、调用业务层和组织响应，不承担行情清洗或 SQL 读写。

### `app/core/`

应用基础配置。

- `config.py`：使用 Pydantic Settings 从 `backend/.env` 和环境变量读取配置，解析数据库绝对路径及 CORS 来源；
- `__init__.py`：包标记。

新增公共配置时应放在 `Settings` 模型中，不要在业务代码中到处读取环境变量。

### `app/database/`

DuckDB 基础设施。

- `connection.py`：创建短连接、关闭连接，并通过进程内写锁串行化写操作；
- `schema.sql`：创建 `stocks`、`daily_bars`、`sync_runs` 表和索引；
- `__init__.py`：导出 `DuckDBDatabase`。

三张表的用途：

- `stocks`：证券代码、名称、交易所和数据源；
- `daily_bars`：不复权日 K，主键为股票、交易日和复权方式；
- `sync_runs`：同步模式、运行状态、成功/失败数量和错误摘要。

### `app/providers/`

外部行情数据源适配层。

- `base.py`：定义 `MarketDataProvider` 抽象接口；
- `hithink.py`：调用同花顺 Financial API，完成股票目录分页、历史日 K 请求、认证、重试和原始字段转换；
- `__init__.py`：导出当前 provider。

如果将来接入其他行情源，应新增 provider 实现 `MarketDataProvider`，不应修改 repository。

### `app/repositories/`

DuckDB 数据访问层。

- `market_data.py`：股票主数据和日 K 的幂等 upsert、行情查询、最新日期查询、同步状态读写；
- `__init__.py`：导出 `MarketDataRepository`。

所有业务 SQL 应集中在 repository 中。其他层通过方法调用读写数据，不直接依赖表结构。

### `app/services/`

业务逻辑与数据清洗层。

- `market_data.py`：确定同步股票池和时间窗口，并发调用 provider，校验 OHLCV，调用 repository 入库；
- `__init__.py`：导出 service 和同步冲突异常。

支持四种同步模式：

- `initial`：初始化最近一年；
- `daily`：从本地最新日期向前回看 5 个自然日后增量更新；
- `weekly`：重新抓取最近 60 个交易日；
- `monthly`：重新抓取最近一年。

同一进程中只允许一个同步任务运行。单只股票失败不会中断其他股票，失败摘要写入 `sync_runs`。

### `app/jobs/`

自动任务层。

- `scheduler.py`：注册每日增量、每周 60 个交易日校准和每月一年期校准；
- `tasks.py`：统一执行同步并记录成功、冲突或异常日志；
- `__init__.py`：导出调度器工厂。

默认计划：

- 周一至周五 18:00：`daily`；
- 周六 09:00：`weekly`；
- 每月 1 日 10:00：`monthly`。

### `app/schemas/`

Pydantic API 数据模型。

- `market.py`：定义股票、日 K、行情响应、市场状态和任务受理响应；
- `__init__.py`：统一导出模型。

schemas 用于稳定 API 契约，不负责数据库写入或 Pandas 清洗。

## `scripts/`：命令行工具

### `scripts/init_db.py`

创建 `data/market.duckdb` 并执行 `schema.sql`。重复执行是安全的。

```bash
PYTHONPATH=. .venv/bin/python backend/scripts/init_db.py
```

### `scripts/sync_market_data.py`

手动同步入口。支持指定模式、股票和试跑数量。

```bash
# 两只股票初始化
PYTHONPATH=. .venv/bin/python backend/scripts/sync_market_data.py \
  --mode initial --symbols 000001,600519

# 全市场每日增量
PYTHONPATH=. .venv/bin/python backend/scripts/sync_market_data.py --mode daily

# 前 20 只股票试跑
PYTHONPATH=. .venv/bin/python backend/scripts/sync_market_data.py \
  --mode initial --limit 20
```

### `scripts/run_scheduler.py`

脱离 FastAPI 单独运行 APScheduler，适合只需要后台数据更新、不需要启动 HTTP API 的部署方式。

### `scripts/__init__.py`

将 scripts 声明为 Python 包，使项目安装后能够稳定导入脚本入口。

## `tests/`：测试

### `tests/test_market_data.py`

使用不访问网络的 fake provider 验证：

- 初始化任务可重复执行且不会产生重复日 K；
- 每日任务会按预期回看近期日期；
- 股票主数据和行情能够正确写入、查询。

### `tests/__init__.py`

测试包标记。

运行测试：

```bash
PYTHONPATH=. .venv/bin/python -m pytest
```

## 数据文件

实际数据库位于项目根目录：

```text
data/market.duckdb
```

该文件包含本地股票主数据、日 K 和同步记录，不包含 API Key。数据库文件属于运行数据，已配置为不提交 Git。

## 新功能应放在哪里

| 需求 | 目录 |
| --- | --- |
| 增加外部数据接口 | `app/providers/` |
| 增加或修改 DuckDB SQL | `app/repositories/` 和 `app/database/schema.sql` |
| 增加清洗、因子准备或同步规则 | `app/services/` |
| 增加 HTTP 接口 | `app/api/` 与 `app/schemas/` |
| 增加定时任务 | `app/jobs/` |
| 增加运维命令 | `scripts/` |
| 增加自动化验证 | `tests/` |

