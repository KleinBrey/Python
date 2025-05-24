

import akshare as ak
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

plt.switch_backend('TkAgg')  # 可选：'Qt5Agg', 'TkAgg', 'WXAgg' 等


# 1. 获取股票数据（示例：贵州茅台 sh600519）
symbol = "sh600519"  # 股票代码，沪市股票前缀sh，深市股票前缀sz
stock_data = ak.stock_zh_a_daily(symbol=symbol,  start_date = "20250101",
    end_date= "21000118",adjust="qfq")  # qfq: 前复权

# 2. 数据清洗与格式化
# 重命名列名，使其符合 mplfinance 的要求
stock_data = stock_data.rename(columns={
    'date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
stock_data.index = pd.to_datetime(stock_data['Date'])  # 将日期设为索引
stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]  # 保留需要的列

# 3. 绘制K线图
# 设置样式和参数
mpf_style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mpf.make_marketcolors(up='r', down='g'))
kwargs = dict(
    type='candle',
    style=mpf_style,
    title=f'股票K线图 - {symbol}',
    ylabel='价格',
    volume=True,
    figratio=(12, 6),
    figscale=1.2,
    mav=(5, 10, 20),  # 添加5日、10日、20日均线
    datetime_format='%Y-%m-%d'
)

# 绘图
mpf.plot(stock_data, **kwargs)
plt.show()