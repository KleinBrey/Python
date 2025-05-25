import finplot as fplt
import numpy as np
import pandas as pd


# 1. 生成模拟数据（30个交易日）
date_rng = pd.date_range(start='2024-01-01', periods=30, freq='B')  # B=工作日
np.random.seed(42)

# 创建价格序列（随机游走）
price = 100 + np.cumsum(np.random.randn(30) * 2)
opens = price + np.random.randn(30)
highs = opens + np.abs(np.random.randn(30) * 3)
lows = opens - np.abs(np.random.randn(30) * 3)
closes = price + np.random.randn(30)

# 创建成交量（随机生成）
volumes = np.random.randint(10000, 50000, size=30)

# 构建DataFrame
mock_data = pd.DataFrame({
    'open': np.round(opens, 2),
    'high': np.round(highs, 2),
    'low': np.round(lows, 2),
    'close': np.round(closes, 2),
    'volume': volumes
}, index=date_rng)

# 2. 创建交互式图表
ax, ax_vol = fplt.create_plot(
    title='模拟股票K线分析',
    rows=2,  # 主图+成交量
    init_zoom_periods=15,  # 初始显示15个周期
)

# 3. 绘制K线（蜡烛图）
fplt.candlestick_ochl(mock_data[['open', 'close', 'high', 'low']])

# 4. 添加5日/20日均线
mock_data['ma5'] = mock_data['close'].rolling(5).mean()
mock_data['ma20'] = mock_data['close'].rolling(20).mean()
fplt.plot(mock_data['ma5'], color='#FF9900', legend='MA5')
fplt.plot(mock_data['ma20'], color='#0099FF', legend='MA20')

# 5. 绘制成交量（柱状图）
fplt.volume_ocv(mock_data[['open', 'close', 'volume']], ax=ax_vol)


# 6. 添加交互功能
def update_legend_text(x, y):
    '''实时显示价格'''
    try:
        row = mock_data.loc[x]
        return f'''日期: {x:%Y-%m-%d}
开盘: {row.open:.2f}
最高: {row.high:.2f}
最低: {row.low:.2f}
收盘: {row.close:.2f}
成交量: {row.volume:,}'''
    except KeyError:
        return ''


fplt.add_legend(update_legend_text, ax=ax)  # 鼠标悬停显示

# 7. 样式调整 (可选)
fplt.candle_bull_color = '#E74C3C'  # 上涨红色
fplt.candle_bear_color = '#2ECC71'  # 下跌绿色
fplt.background = '#FFFFFF'  # 白色背景
fplt.foreground = '#333333'  # 深灰文字
fplt.legend_border_color = '#CCCCCC'  # 图例边框

# 显示图表
fplt.show()
