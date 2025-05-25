import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# 生成模拟股票数据
def generate_stock_data(stock_name, days=30, start_price=100):
    date_index = pd.date_range(end=datetime.today(), periods=days, freq='D')

    # 生成价格序列
    fluctuations = np.random.normal(0, 1.5, days)
    close_prices = np.round(start_price + np.cumsum(fluctuations), 2)

    # 生成OHLC数据
    data = {
        'Open': close_prices + np.random.uniform(-1, 1, days),
        'High': close_prices + np.random.uniform(0, 2, days),
        'Low': close_prices - np.random.uniform(0, 2, days),
        'Close': close_prices,
        'Volume': np.random.randint(10000, 50000, days)
    }

    df = pd.DataFrame(data, index=date_index)
    df['High'] = df[['Open', 'Close', 'High']].max(axis=1)
    df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1)

    return df


# 生成3只股票数据
stock1 = generate_stock_data('AAPL', start_price=150)
stock2 = generate_stock_data('GOOG', start_price=2800)
stock3 = generate_stock_data('TSLA', start_price=700)

# 创建3行1列的子图布局
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
plt.subplots_adjust(hspace=0.3)

# 绘制第一只股票
mpf.plot(stock1,
         type='candle',
         volume=True,
         style='yahoo',
         ax=axes[0],
         volume_panel=1,
         panel_ratios=(3, 1),
         axtitle='AAPL')

# 绘制第二只股票
mpf.plot(stock2,
         type='candle',
         volume=True,
         style='yahoo',
         ax=axes[1],
         volume_panel=1,
         panel_ratios=(3, 1),
         axtitle='GOOG')

# 绘制第三只股票
mpf.plot(stock3,
         type='candle',
         volume=True,
         style='yahoo',
         ax=axes[2],
         volume_panel=1,
         panel_ratios=(3, 1),
         axtitle='TSLA')

# 设置总标题
fig.suptitle('Stock Analysis - Triple Chart', y=0.92, fontsize=16)

# 调整底部空间防止日期重叠
plt.subplots_adjust(bottom=0.1)

# 显示图表
plt.show()