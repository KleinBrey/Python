# 导入tushare
import tushare as ts

# 初始化pro接口
pro = ts.pro_api('b84edc56c8bee18697958fe5b8105df277a2179fee7966e026e57df6')

# 拉取数据
df = pro.daily(**{
    "ts_code": "002115.SZ",
    "trade_date": "",
    "start_date": 20250701,
    "end_date": 20250830,
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount"
])
print(df)

