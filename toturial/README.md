# Python 从零基础到日常开发：案例式教程

这套教程面向“会一点 JavaScript / React、正在系统学习 Python”的初学者，目标环境是 **Python 3.11+**。所有 `.py` 案例都可单独运行，默认不访问网络、不修改项目业务数据；需要第三方库的章节在缺少依赖时会给出安装提示。

## 如何学习

先确认版本：

```bash
python3 --version
```

从 `01_basics` 开始，按目录编号、再按文件编号学习：

```bash
cd study/01_basics
python 00_hello_python.py
python 01_variables.py
```

建议每节按这个节奏：

1. 先阅读文件顶部目标和中文注释。
2. 运行文件，观察实际输出。
3. 修改数据，预测结果后再运行。
4. 遇到“练习”先自己完成，再看参考答案。
5. 完成一章后用自己的场景重写一个小案例。

安装全部可选学习依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r study/14_engineering/requirements-learning.txt
```

Windows 激活命令是 `.venv\Scripts\activate`。标准库章节不需要安装第三方包。

## Python 学习路线

### 阶段 1：基础语法

学习 `01_basics` 和 `02_strings`：输出、变量、基本类型、数值、布尔值、`None`、类型转换、运算符、输入、字符串和 f-string。

完成标准：能读取简单输入，转换类型，并格式化输出一条股票信息。

### 阶段 2：数据结构

学习 `03_collections`：`list`、`tuple`、`dict`、`set`，以及它们的选型原则。

完成标准：能用“字典列表”表示多只股票并完成增加、删除、查找、排序和筛选。

### 阶段 3：流程控制

学习 `04_control_flow`：`if`、`match`、`for`、`while`、`range`、`enumerate`、`zip`、`break`、`continue` 和 `pass`。

完成标准：能遍历行情数据，筛选目标并为结果编号。

### 阶段 4：函数

学习 `05_functions`：定义与调用、注解、各种参数、解包、多返回值、作用域、lambda、高阶函数和回调。

完成标准：能把重复逻辑拆成职责清楚、输入输出明确的函数。

### 阶段 5：面向对象

学习 `06_modules_oop` 和 `07_exceptions`：模块、包、入口保护、类与对象、方法种类、继承、多态、封装、抽象类和异常体系。

完成标准：能设计一个 `Stock` 类和一个可替换实现的 `MarketDataProvider`。

### 阶段 6：Python 高级特性

学习 `08_advanced`：装饰器、迭代器、生成器、上下文管理器、现代类型注解、`Protocol`、泛型、dataclass 和正则。

完成标准：能读懂现代 Python 项目中常见的 `@decorator`、`yield`、`with` 和复杂注解。

### 阶段 7：文件 / API / 数据库

学习 `09_io_stdlib`、`10_concurrency`、`11_http_packages`、`12_databases`：文件、JSON、CSV、日期时区、日志、命令行、并发、HTTP、包管理、Pydantic、SQLite 和 DuckDB。

完成标准：能安全读取外部数据、校验数据、记录日志并存入数据库。

### 阶段 8：Pandas

学习 `13_pandas`：Series、DataFrame、CSV、检查、选择、筛选、排序、分组、关联、拼接、缺失值、去重和日期。

完成标准：能从 OHLCV 数据计算分组统计、收益率和滚动指标。

### 阶段 9：工程化

学习 `14_engineering`：项目结构、Repository / Service / Provider / Factory、依赖注入、pytest、fixture 和 mock。

完成标准：能解释各层职责，并为不依赖真实网络的业务函数编写测试。

### 阶段 10：实战

依次完成 `projects` 下五个项目。先运行原版，再尝试各项目 README 的扩展练习。

## 完整目录索引

### 01_basics — Python 基础

- `00_hello_python.py`：运行脚本、`print`、注释、缩进。
- `01_variables.py`：变量、赋值、命名和常量约定。
- `02_data_types.py`：`int`、`float`、`str`、`bool`、`None`、`type`、`isinstance`。
- `03_numbers.py`：数字运算、浮点精度和 `Decimal`。
- `04_boolean_none.py`：真值、短路逻辑、`is None`。
- `05_type_conversion.py`：常见转换和转换错误。
- `06_operators.py`：算术、比较、逻辑、赋值、成员和身份运算符。
- `07_input_output.py`：`input`、转换和格式化输出；自动演示可加 `--demo`。

### 02_strings — 字符串

- `00_string_basics.py`：创建、引号、多行文本、索引、切片、不可变性、转义和 raw string。
- `01_string_methods.py`：`len/find/index/replace/split/join/strip/startswith/endswith/upper/lower`。
- `02_f_strings.py`：f-string、`format`、拼接、数字和百分比格式。

### 03_collections — 数据结构

- `00_lists.py`：列表全部常用操作、切片、嵌套、遍历和推导式。
- `01_tuples.py`：元组、不可变性、解包和多返回值。
- `02_dictionaries.py`：字典增删改查、方法、遍历、嵌套和推导式。
- `03_sets.py`：去重、增删和并交差运算。
- `04_collection_choices.py`：四类容器的对比和章节练习。

### 04_control_flow — 流程控制

- `00_conditions.py`：`if/elif/else`、嵌套条件和条件表达式。
- `01_match_case.py`：值匹配与结构模式匹配。
- `02_for_loops.py`：`for/range/enumerate/zip/items` 和 `for...else`。
- `03_while_break_continue.py`：`while/break/continue/pass` 和有限重试。

### 05_functions — 函数

- `00_function_basics.py`：定义、调用、参数、`return` 和函数注解。
- `01_parameters.py`：默认/位置/关键字参数、`*args`、`**kwargs` 和可变默认值。
- `02_unpacking_returns.py`：`*`/`**` 参数解包、多返回值和字典合并。
- `03_scope.py`：LEGB、局部/全局变量、`global` 和 `nonlocal`。
- `04_higher_order.py`：lambda、map、filter、sorted、高阶函数和回调。

### 06_modules_oop — 模块、包与 OOP

- `00_imports_and_modules.py`：import、别名、查找机制、`__name__` 和入口保护。
- `example_package/`、`01_package_demo.py`：自编模块、包、`__init__.py` 和公开入口。
- `02_class_objects.py`：类、对象、`self`、`__init__`、实例/类变量和实例方法。
- `03_method_types.py`：实例方法、`@classmethod` 和 `@staticmethod`。
- `04_inheritance_polymorphism.py`：继承、`super`、重写和多态。
- `05_encapsulation_properties.py`：封装、单/双下划线、property、getter 和 setter。
- `06_dunder_methods.py`：`__str__` 与 `__repr__`。
- `07_abstract_classes.py`：`ABC`、`abstractmethod` 和接口思想。

### 07_exceptions — 异常

- `00_exception_basics.py`：`try/except/else/finally` 和常见内置异常。
- `01_raise_custom.py`：`raise`、自定义异常、`RuntimeError` 和异常链。

### 08_advanced — 高级特性与类型

- `00_decorators.py`：函数对象、闭包、装饰器、带参数装饰器和 `wraps`。
- `01_iterators_generators.py`：iterable、iterator、`iter/next/yield` 和生成器表达式。
- `02_context_managers.py`：`with`、`__enter__/__exit__` 和 `contextmanager`。
- `03_typing_basics.py`：容器类型、联合类型、Any、Optional、Union、Literal、Callable、TypeAlias 和 future annotations。
- `04_typing_protocol_generic.py`：Protocol、Generic 和 TypeVar。
- `05_dataclasses.py`：dataclass、`field/default_factory`、`__post_init__` 和普通类对比。
- `06_regex.py`：`search/match/findall/sub/split/group` 与简单邮箱、手机号、股票代码案例。

### 09_io_stdlib — 文件和常用标准库

- `00_pathlib_files.py`：open/read/readline/readlines/write/append/with/encoding 与 Path API。
- `01_json.py`：`loads/dumps/load/dump` 与 JSON ↔ dict。
- `02_csv.py`：CSV 字典式读写与类型转换。
- `03_datetime_timezone.py`：date/time/datetime/timedelta/ZoneInfo/UTC/格式转换。
- `04_math_random_statistics.py`：数学、模拟随机与基础统计。
- `05_collections_itertools.py`：Counter/defaultdict/deque 与 itertools。
- `06_functools_cache.py`：`lru_cache`、partial、reduce 和缓存边界。
- `07_os_sys_time.py`：操作系统、解释器、环境变量、时间戳和性能计时。
- `08_logging.py`：五个日志级别、格式、模块 logger 和异常日志。
- `09_argparse_cli.py`：位置/可选参数、default/type/choices/action/help。

### 10_concurrency — 并发

- `00_concepts.py`：普通执行以及同步/异步/并发/并行的区别。
- `01_threading_demo.py`：Thread、start、join、daemon、Lock 和非固定顺序。
- `02_multiprocessing_demo.py`：多进程池、CPU 密集任务和入口保护。
- `03_asyncio_demo.py`：`async def/await/asyncio.run/gather`。

### 11_http_packages — HTTP、包管理与 Pydantic

- `00_http_requests.py`：GET/POST、query、headers、JSON body、状态码、超时和异常；加 `--live` 才联网。
- `01_package_management.py`：pip、venv、requirements 和 pyproject.toml。
- `02_pydantic_models.py`：BaseModel、Field、validation、field_validator、model_dump/model_validate。
- `03_pydantic_settings.py`：BaseSettings、SettingsConfigDict、环境变量和 `.env` 思想。

### 12_databases — 数据库

- `00_sqlite_crud.py`：建库建表、INSERT/SELECT/UPDATE/DELETE、参数化 SQL 和事务。
- `01_duckdb_basics.py`：DuckDB 连接、表、插入和分析查询。
- `02_duckdb_pandas.py`：DataFrame 注册、SQL 查询和结果转 DataFrame。

### 13_pandas — 数据分析

- `00_series_dataframe.py`：Series、DataFrame、创建、head/tail/columns/index/dtypes。
- `01_read_csv_inspect.py`：CSV、dtype、日期解析、info/describe/shape。
- `02_selection_filter_sort.py`：loc、iloc、条件筛选、sort_values 和安全赋值。
- `03_groupby_aggregate.py`：groupby、agg 和 transform。
- `04_merge_concat_apply.py`：merge、concat、apply 和向量化意识。
- `05_cleaning_dates.py`：缺失值、dropna/fillna、去重和日期处理。

### 14_engineering — 工程化与测试

- `00_project_structure.py`：api/core/database/models/providers/repositories/services/scripts/tests 职责。
- `01_design_patterns.py`：Repository、Service Layer、Provider、Factory、Singleton 思想和依赖注入。
- `calculator.py`：被测业务模块。
- `test_calculator.py`：pytest、assert、发现规则和基础测试。
- `test_fixtures_mock.py`：fixture、fake、mock 和 `pytest.approx`。
- `requirements-learning.txt`：本教程的可选第三方依赖。

### projects — 综合实战

- `01_student_system`：学生成绩管理，综合 class/list/JSON/pathlib。
- `02_stock_manager`：A 股行情管理，综合 dataclass/typing/Provider/Service/Repository/SQLite/logging/exception。
- `03_file_data_analysis`：CSV 分组统计并输出 JSON。
- `04_api_client`：可注入、可测试、带 timeout 思想的 API 客户端。
- `05_stock_data_analysis`：Pandas + DuckDB 的收益率、均线与 SQL 汇总分析。

## 测试与自检

运行教学测试：

```bash
python -m pytest study/14_engineering/test_calculator.py \
  study/14_engineering/test_fixtures_mock.py -v
```

编译检查全部文件：

```bash
python -m compileall -q study
```

`study/threads.py` 是项目中原本存在的文件，本教程没有覆盖它；线程的系统课程请阅读 `10_concurrency/01_threading_demo.py`。

## 继续进阶

完成五个项目后，可以选择一个方向深入：Web API（FastAPI）、数据工程（Pandas/Polars/DuckDB）、自动化脚本、量化研究或测试与工程工具。此时再引入框架会更容易理解，因为你已经掌握了函数、对象、异常、类型、I/O 和依赖分层这些共同基础。
