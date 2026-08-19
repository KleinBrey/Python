可以把这些 SQL 关键字理解成：**查数据、筛数据、组合数据、统计数据、修改数据、删除数据、插入数据**的一套指令。

你现在用 DuckDB 做股票数据库，这些基本就是最常用的一批 SQL。

## 1. `SELECT` —— 我要哪些数据

`SELECT` 用来指定**你想查询哪些字段**。

例如：

```sql
SELECT symbol, close, volume
FROM daily_bars;
```

意思是：

> 从 `daily_bars` 里查询 `symbol`、`close`、`volume` 三个字段。

如果全部字段都要：

```sql
SELECT *
FROM daily_bars;
```

`*` 表示所有列。

还可以计算：

```sql
SELECT
    symbol,
    close,
    volume,
    close * volume AS value
FROM daily_bars;
```

`AS value` 是给计算结果起一个临时名字。

---

## 2. `FROM` —— 数据从哪里来

`FROM` 指定**查询哪张表**。

```sql
SELECT *
FROM daily_bars;
```

就是：

> 我要查询数据，数据来源是 `daily_bars`。

通常：

```sql
SELECT ...
FROM ...
```

是最基本的 SQL 查询结构。

例如你的股票表：

```sql
SELECT *
FROM stocks;
```

---

# 3. `WHERE` —— 筛选哪些行

`WHERE` 用来**过滤数据**。

例如：

```sql
SELECT *
FROM daily_bars
WHERE symbol = '601899';
```

意思是：

> 只查询 `601899` 这只股票。

多个条件：

```sql
SELECT *
FROM daily_bars
WHERE symbol = '601899'
  AND date >= DATE '2026-08-01';
```

也可以使用：

```sql
WHERE close > 20
```

```sql
WHERE volume >= 1000000
```

```sql
WHERE source = 'Tushare'
```

常见逻辑：

```sql
AND
OR
NOT
```

例如：

```sql
SELECT *
FROM stocks
WHERE market = '主板'
  AND exchange = 'SH';
```

---

# 4. `ORDER BY` —— 排序

`ORDER BY` 用来给查询结果排序。

例如按收盘价从低到高：

```sql
SELECT *
FROM daily_bars
ORDER BY close ASC;
```

`ASC`：

> ascending，升序

例如：

```text
10
20
30
40
```

按收盘价从高到低：

```sql
SELECT *
FROM daily_bars
ORDER BY close DESC;
```

`DESC`：

> descending，降序

结果类似：

```text
40
30
20
10
```

股票数据特别常用：

```sql
SELECT *
FROM daily_bars
WHERE symbol = '601899'
ORDER BY date DESC;
```

意思就是：

> 查 601899，并且最新交易日在最前面。

---

# 5. `LIMIT` —— 只要前几条

`LIMIT` 限制返回的数据数量。

例如：

```sql
SELECT *
FROM daily_bars
LIMIT 10;
```

只返回前 10 行。

和 `ORDER BY` 配合就很好用。

例如找成交额最大的 10 条记录：

```sql
SELECT *
FROM daily_bars
ORDER BY amount DESC
LIMIT 10;
```

可以理解为：

> 先按成交额从大到小排序，再取前 10 个。

你以后做量化筛选会经常使用：

```sql
SELECT *
FROM stocks
ORDER BY market_cap DESC
LIMIT 100;
```

---

# 6. `GROUP BY` —— 分组统计

这个非常重要。

`GROUP BY` 的作用是：

> **按照某个字段把数据分成一组一组，然后进行统计。**

例如你的 `daily_bars`：

```text
symbol    date          volume
601899    2026-08-17    100
601899    2026-08-18    200
600519    2026-08-17    300
600519    2026-08-18    500
```

现在要计算每只股票总成交量：

```sql
SELECT
    symbol,
    SUM(volume) AS total_volume
FROM daily_bars
GROUP BY symbol;
```

结果：

```text
symbol    total_volume
601899    300
600519    800
```

也就是说：

```sql
GROUP BY symbol
```

表示：

> 按股票代码分组。

然后：

```sql
SUM(volume)
```

计算每组的成交量总和。

常见聚合函数：

| 函数        | 功能  |
| --------- | --- |
| `SUM()`   | 求和  |
| `AVG()`   | 平均值 |
| `MAX()`   | 最大值 |
| `MIN()`   | 最小值 |
| `COUNT()` | 数量  |

例如：

```sql
SELECT
    symbol,
    AVG(close) AS avg_close,
    MAX(close) AS max_close,
    MIN(close) AS min_close
FROM daily_bars
GROUP BY symbol;
```

这已经非常接近量化分析了。

---

# 7. `HAVING` —— 对分组后的结果再筛选

`HAVING` 很容易和 `WHERE` 搞混。

区别记住：

> **WHERE 筛原始数据。**
>
> **HAVING 筛 GROUP BY 之后的统计结果。**

例如：

```sql
SELECT
    symbol,
    AVG(volume) AS avg_volume
FROM daily_bars
GROUP BY symbol
HAVING AVG(volume) > 1000000;
```

意思：

> 先按照股票分组 → 计算每只股票平均成交量 → 只保留平均成交量超过 100 万的股票。

为什么不能直接：

```sql
WHERE AVG(volume) > 1000000
```

因为 `WHERE` 执行的时候，还没有完成 `GROUP BY`，`AVG(volume)` 这个结果还不存在。

一个比较典型的结构：

```sql
SELECT
    symbol,
    AVG(volume) AS avg_volume
FROM daily_bars
WHERE date >= DATE '2026-08-01'
GROUP BY symbol
HAVING AVG(volume) > 1000000;
```

这里：

```text
WHERE
↓
先过滤交易日期

GROUP BY
↓
按照股票分组

HAVING
↓
再过滤统计结果
```

---

# 8. `JOIN` —— 把两张表拼起来

这个对于你的股票系统以后会**非常重要**。

假设你有：

### `stocks`

```text
symbol    name       market
601899    紫金矿业    主板
600519    贵州茅台    主板
```

以及：

### `daily_bars`

```text
symbol    date          close
601899    2026-08-18    25.60
600519    2026-08-18    1450
```

你想同时看到：

```text
股票代码 + 股票名称 + 收盘价
```

就需要 `JOIN`：

```sql
SELECT
    stocks.symbol,
    stocks.name,
    daily_bars.close
FROM stocks
JOIN daily_bars
    ON stocks.symbol = daily_bars.symbol;
```

相当于通过：

```text
stocks.symbol
        ↓
      对应
        ↓
daily_bars.symbol
```

把两张表关联起来。

实际项目中更常写别名：

```sql
SELECT
    s.symbol,
    s.name,
    d.date,
    d.close
FROM stocks AS s
JOIN daily_bars AS d
    ON s.symbol = d.symbol;
```

这里：

```text
s = stocks
d = daily_bars
```

以后你的量化系统里可能会有：

```text
stocks
daily_bars
financials
indicators
stock_tags
industry
```

这些表之间大量都会靠 `JOIN` 关联。

最常见的是：

```sql
INNER JOIN
LEFT JOIN
```

其中你目前优先学会 `LEFT JOIN` 和普通 `JOIN` 就够了。

---

# 9. `UPDATE` —— 修改已有数据

`UPDATE` 用来修改数据库中**已经存在的行**。

例如：

```sql
UPDATE daily_bars
SET close = 25.60
WHERE symbol = '601899';
```

意思：

> 把 601899 的 `close` 改成 25.60。

但是这个 SQL 有危险 ⚠️：

```sql
WHERE symbol = '601899'
```

会修改 `601899` **所有日期**的数据。

所以通常应该：

```sql
UPDATE daily_bars
SET close = 25.60
WHERE symbol = '601899'
  AND date = DATE '2026-08-18';
```

这样才是：

> 修改 601899 在 2026-08-18 这一天的数据。

---

# 10. `SET` —— UPDATE 到底修改什么

`SET` 一般跟着 `UPDATE` 使用。

例如：

```sql
UPDATE daily_bars
SET close = 25.60,
    amount = 25400000,
    update_time = now()
WHERE symbol = '601899'
  AND date = DATE '2026-08-18';
```

可以拆成：

```text
UPDATE daily_bars
```

选择要修改的表。

```text
SET
```

指定修改什么。

```text
WHERE
```

指定修改哪几行。

所以：

```sql
UPDATE
SET
WHERE
```

基本是一套组合。

---

# 11. `DELETE` —— 删除数据

`DELETE` 删除数据库中的行。

例如：

```sql
DELETE FROM daily_bars
WHERE symbol = '601899';
```

表示：

> 删除 601899 的所有日线数据。

例如你刚才使用的：

```sql
DELETE FROM daily_bars
WHERE source = 'Tushare';
```

就是：

> 删除所有来源为 Tushare 的日线数据。

### ⚠️ 特别注意

如果写：

```sql
DELETE FROM daily_bars;
```

就是：

> **整张表的数据全部删除。**

表还在，但是数据全部没了。

所以使用 `DELETE` 时一定特别注意 `WHERE`。

一般建议先：

```sql
SELECT *
FROM daily_bars
WHERE source = 'Tushare';
```

确认没问题，再：

```sql
DELETE FROM daily_bars
WHERE source = 'Tushare';
```

---

# 12. `INSERT` —— 插入新数据

`INSERT` 是向表中添加新的数据。

例如：

```sql
INSERT INTO stocks (
    symbol,
    name,
    exchange,
    source
)
VALUES (
    '601899',
    '紫金矿业',
    'SH',
    'Tushare'
);
```

意思就是插入一条新股票。

简单理解：

```text
INSERT INTO
    ↓
插到哪张表

(symbol, name, ...)
    ↓
哪些字段

VALUES (...)
    ↓
具体是什么值
```

也可以批量：

```sql
INSERT INTO stocks (
    symbol,
    name,
    exchange,
    source
)
VALUES
    ('601899', '紫金矿业', 'SH', 'Tushare'),
    ('600519', '贵州茅台', 'SH', 'Tushare'),
    ('000001', '平安银行', 'SZ', 'Tushare');
```

不过你现在 Python + Pandas + DuckDB 的项目中，大批量数据通常不会手动一条条 `INSERT`，而是直接批量写 `DataFrame`。

---

# 把它们串起来看

以后你会经常看到这种完整 SQL：

```sql
SELECT
    d.symbol,
    s.name,
    AVG(d.volume) AS avg_volume,
    AVG(d.close) AS avg_close
FROM daily_bars AS d
JOIN stocks AS s
    ON d.symbol = s.symbol
WHERE d.date >= DATE '2026-08-01'
GROUP BY
    d.symbol,
    s.name
HAVING AVG(d.volume) > 1000000
ORDER BY avg_volume DESC
LIMIT 20;
```

翻译成人话就是：

```text
FROM
↓
从 daily_bars 获取数据

JOIN
↓
把 stocks 股票信息关联进来

WHERE
↓
只看 8 月 1 日之后的数据

GROUP BY
↓
按照股票进行分组

HAVING
↓
只保留平均成交量 > 100 万的股票

SELECT
↓
我要股票代码、名称、平均成交量、平均价格

ORDER BY
↓
按照平均成交量从大到小排序

LIMIT
↓
只取前 20 只
```

---

## 最值得你记住的一张关系图

```text
查询：

SELECT      我要什么
FROM        从哪里拿
JOIN        和谁关联
WHERE       原始数据怎么筛
GROUP BY    怎么分组
HAVING      分组后怎么筛
ORDER BY    怎么排序
LIMIT       最后取多少条


修改：

UPDATE      修改哪张表
SET         修改成什么
WHERE       修改哪些行


新增：

INSERT INTO 向哪张表插数据
VALUES      插入什么数据


删除：

DELETE FROM 删除哪张表的数据
WHERE       删除哪些行
```

对于你现在的 **DuckDB + 股票量化数据库**，优先把 `SELECT / FROM / WHERE / ORDER BY / LIMIT` 掌握熟，然后学 `GROUP BY + 聚合函数`，最后重点掌握 `JOIN`。这几块会覆盖你以后绝大多数选股和行情查询场景。
