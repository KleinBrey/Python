# 导入tushare
import mplfinance as mpf
import pandas as pd
from mongodb import database
from data_source import tushare


def save_daily_to_mongo(ts_codes, start_date, end_date):
    """
    批量获取股票日线行情并存储到 MongoDB
    :param ts_codes: 股票代码字符串, 例 "000001.SZ,600000.SH"
    :param start_date: 开始日期, 例 "20180701"
    :param end_date: 结束日期, 例 "20180718"
    """
    df = tushare.daily(ts_code=ts_codes, start_date=start_date, end_date=end_date)

    if df.empty:
        print("没有获取到数据")
        return

    # DataFrame 转 dict
    records = df.to_dict("records")

    # 插入 MongoDB
    if records:
        database.stock_daily_data.insert_many(records)
        print(f"成功插入 {len(records)} 条记录到 MongoDB")

    return df


df = save_daily_to_mongo(
    ts_codes="600519.SH",
    start_date="20250101",
    end_date="20301010"
)

print(df.head())

# 2. 数据清洗与格式化
# 重命名列名，使其符合 mplfinance 的要求

df = df.sort_values(by='trade_date', ascending=True)
stock_data = df.rename(columns={
    'trade_date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'vol': 'Volume'
})
stock_data.index = pd.to_datetime(stock_data['Date'])  # 将日期设为索引
stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]  # 保留需要的列

# 3. 绘制K线图
# 设置样式和参数
custom_style = mpf.make_mpf_style(
    base_mpf_style='yahoo',  # 基础样式
    rc={'font.family': 'Hei', 'font.size': 12, },
    marketcolors=mpf.make_marketcolors(
        up='red',
        down='green',
        edge='#1A1A1A',  # 深灰色边框
        wick={'up': 'red', 'down': 'green'},  # 渐变色影线
        volume={'up': 'red', 'down': 'green'},  # 成交量颜色
        alpha=0.8  # 颜色透明度
    ),
    gridstyle=':',  # 虚线网格
    gridcolor='lightgray',  # 浅灰色网格
    facecolor='white',  # 图表背景色
    edgecolor='black',  # 图表边框色
    figcolor='white'  # 画布背景色
)
kwargs = dict(
    type='candle',
    style=custom_style,
    title=f'{'fgfgg'}{'666'}日K线图',
    ylabel='价格',
    ylabel_lower='成交量',  # 成交量面板标签
    volume=True,
    figratio=(12, 6),
    figscale=1.2,
    panel_ratios=(4, 1),  # 主图与成交量图高度比 4:1
    scale_padding={'left': 0.2, 'right': 0.8, 'top': 0.8, 'bottom': 0.6},  # 坐标轴缩放边距
    mav=(5, 10, 20),  # 添加5日、10日、20日均线
    show_nontrading=False,  # 不展示非交易日
    datetime_format='%Y-%m-%d',
    xrotation=0,  # X轴标签旋转角度
    update_width_config=dict(
        candle_linewidth=0.5,  # K线边框粗细
        candle_width=0.8,  # K线宽度（0.8=80%的默认宽度）
        volume_width=0.7  # 成交量柱宽
    ),

)

# 绘图
mpf.plot(stock_data, **kwargs)
