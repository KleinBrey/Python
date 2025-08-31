import akshare as ak
import pandas as pd
from pyecharts.charts import Kline, Line
from pyecharts import options as opts
import datetime
import os
from utils.open_file_in_browser import open_file_in_browser


def get_stock_data(stock_code, period="daily", adjust="qfq", start_date=None, end_date=None):
    """
    获取股票数据

    Args:
        stock_code: 股票代码，如 "000001"
        period: 周期，daily/weekly/monthly
        adjust: 复权类型，qfq前复权/hfq后复权/""不复权
        start_date: 开始日期 "20240101"
        end_date: 结束日期 "20241231"
    """
    try:
        # 获取股票历史数据
        if start_date and end_date:
            stock_data = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
        else:
            stock_data = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                adjust=adjust
            )

        # 数据预处理
        stock_data['日期'] = pd.to_datetime(stock_data['日期'])
        stock_data = stock_data.sort_values('日期')
        stock_data.reset_index(drop=True, inplace=True)

        return stock_data

    except Exception as e:
        print(f"获取股票 {stock_code} 数据失败: {e}")
        return None


def calculate_ma(data, window):
    """计算移动平均线"""
    return data['收盘'].rolling(window=window).mean().tolist()


def create_simple_kline_chart(stock_data, stock_code, stock_name=""):
    """
    创建简化版K线图（兼容性更好）

    Args:
        stock_data: 股票数据DataFrame
        stock_code: 股票代码
        stock_name: 股票名称
    """

    # 准备K线数据
    kline_data = []
    dates = []

    for index, row in stock_data.iterrows():
        dates.append(row['日期'].strftime('%Y-%m-%d'))
        kline_data.append([
            float(row['开盘']),  # 开盘价
            float(row['收盘']),  # 收盘价
            float(row['最低']),  # 最低价
            float(row['最高'])  # 最高价
        ])

    # 计算移动平均线
    ma5 = calculate_ma(stock_data, 5)
    ma10 = calculate_ma(stock_data, 10)
    ma20 = calculate_ma(stock_data, 20)

    # 创建K线图
    kline = (
        Kline(init_opts=opts.InitOpts(width="1400px", height="800px"))
        .add_xaxis(dates)
        .add_yaxis(
            series_name="K线",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",  # 阳线颜色（红色）
                color0="#14b143",  # 阴线颜色（绿色）
                border_color="#ef232a",
                border_color0="#14b143",
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{stock_name}({stock_code}) K线图",
                subtitle="基于akshare数据源 | 包含5日、10日、20日均线",
                pos_left="center"
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    range_start=70,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    range_start=70,
                    range_end=100,
                ),
            ],
            legend_opts=opts.LegendOpts(
                is_show=True,
                pos_top=40
            ),
        )
    )

    # 创建移动平均线
    line = (
        Line()
        .add_xaxis(dates)
        .add_yaxis(
            series_name="MA5",
            y_axis=ma5,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2, color="#FF6B6B"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA10",
            y_axis=ma10,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2, color="#4ECDC4"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA20",
            y_axis=ma20,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(width=2, color="#45B7D1"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
        )
    )

    # 合并K线图和移动平均线
    kline.overlap(line)

    return kline


def process_single_stock(stock_info, start_date, end_date, output_dir):
    """
    处理单个股票的数据和图表生成

    Args:
        stock_info: 股票信息字典，包含 'code' 和 'name'
        start_date: 开始日期
        end_date: 结束日期
        output_dir: 输出目录

    Returns:
        dict: 包含股票统计信息的字典
    """
    stock_code = stock_info['code']
    stock_name = stock_info['name']

    print(f"\n正在处理股票: {stock_name}({stock_code})")
    print("-" * 40)

    # 获取股票数据
    stock_data = get_stock_data(
        stock_code=stock_code,
        period="daily",
        adjust="qfq",
        start_date=start_date,
        end_date=end_date
    )

    if stock_data is None or stock_data.empty:
        print(f"❌ 获取股票 {stock_name}({stock_code}) 数据失败或数据为空")
        return None

    print(f"✅ 成功获取 {len(stock_data)} 条数据")

    # 创建K线图
    print("📊 正在生成K线图...")
    chart = create_simple_kline_chart(stock_data, stock_code, stock_name)

    # 保存图表
    output_file = f"{stock_name}_{stock_code}_kline.html"
    output_path = os.path.join(output_dir, output_file)
    chart.render(output_path)
    print(f"💾 K线图已保存为: {output_path}")

    # 在浏览器中打开
    abs_path = os.path.abspath(output_path)
    open_file_in_browser(abs_path)

    # 计算统计信息
    stats = {
        'name': stock_name,
        'code': stock_code,
        'data_count': len(stock_data),
        'date_range': f"{stock_data['日期'].min().strftime('%Y-%m-%d')} 至 {stock_data['日期'].max().strftime('%Y-%m-%d')}",
        'highest_price': stock_data['最高'].max(),
        'lowest_price': stock_data['最低'].min(),
        'latest_close': stock_data['收盘'].iloc[-1],
        'period_change': ((stock_data['收盘'].iloc[-1] / stock_data['收盘'].iloc[0] - 1) * 100)
    }

    # 显示统计信息
    print(f"\n📈 {stock_name} 数据统计:")
    print(f"   数据时间范围: {stats['date_range']}")
    print(f"   最高价: {stats['highest_price']:.2f}")
    print(f"   最低价: {stats['lowest_price']:.2f}")
    print(f"   最新收盘价: {stats['latest_close']:.2f}")
    print(f"   期间涨跌幅: {stats['period_change']:.2f}%")

    return stats


def main():
    """主函数"""
    # 配置股票列表
    stocks = [

        {"code": "002115", "name": "三维通信"}
    ]

    # 配置日期参数
    start_date = "20250101"
    end_date = "20250830"

    # 创建输出目录
    output_dir = "output-chart"
    os.makedirs(output_dir, exist_ok=True)

    print("🚀 开始批量生成股票K线图")
    print(f"📅 数据时间范围: {start_date} - {end_date}")
    print(f"📊 共需处理 {len(stocks)} 只股票")
    print("=" * 60)

    # 存储所有股票的统计信息
    all_stats = []

    # 逐个处理每只股票
    for i, stock_info in enumerate(stocks, 1):
        print(f"\n[{i}/{len(stocks)}] 开始处理...")
        stats = process_single_stock(stock_info, start_date, end_date, output_dir)

        if stats:
            all_stats.append(stats)
            print(f"✅ {stock_info['name']} 处理完成")
        else:
            print(f"❌ {stock_info['name']} 处理失败")

    # 显示汇总信息
    print("\n" + "=" * 60)
    print(f"🎉 批量处理完成！成功处理 {len(all_stats)} 只股票")

    if all_stats:
        print("\n📊 汇总统计信息:")
        print("-" * 60)
        print(f"{'股票名称':<12} {'代码':<10} {'涨跌幅':<10} {'最新价':<10} {'最高价':<10}")
        print("-" * 60)

        for stats in all_stats:
            print(f"{stats['name']:<12} {stats['code']:<10} {stats['period_change']:>6.2f}% "
                  f"{stats['latest_close']:>8.2f} {stats['highest_price']:>8.2f}")

        print("-" * 60)

        # 找出表现最好和最差的股票
        best_performer = max(all_stats, key=lambda x: x['period_change'])
        worst_performer = min(all_stats, key=lambda x: x['period_change'])

        print(f"\n🏆 期间表现最佳: {best_performer['name']} ({best_performer['period_change']:.2f}%)")
        print(f"📉 期间表现最差: {worst_performer['name']} ({worst_performer['period_change']:.2f}%)")


if __name__ == "__main__":
    # 安装依赖提示
    print("📦 请确保已安装以下依赖包:")
    print("pip install akshare pyecharts pandas")
    print("-" * 50)

    main()