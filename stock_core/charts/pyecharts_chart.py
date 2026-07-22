import os
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Page
from pyecharts.commons.utils import JsCode
from tqdm import tqdm
from stock_core.database import collections as database
from stock_core.utils.open_file_in_browser import open_file_in_browser


def calculate_ma(data, window):
    """计算移动平均线"""
    return data['收盘价'].rolling(window=window).mean().tolist()


def create_kline_chart(stock_data, stock_code, stock_name):
    """
    创建K线图

    Args:
        stock_data: 股票数据DataFrame
        stock_code: 股票代码
        stock_name: 股票名称
    """

    # 日期
    dates = []
    # K线
    kline_data = []
    # 成交量
    volumes = []

    for index, row in stock_data.iterrows():
        dates.append(row['交易日期'])
        kline_data.append([
            float(row['开盘价']),  # 开盘价
            float(row['收盘价']),  # 收盘价
            float(row['最低价']),  # 最低价
            float(row['最高价'])  # 最高价
        ])
        volumes.append({
            "value": float(row['成交量']),
            "open": float(row['开盘价']),
            "close": float(row['收盘价']),
        })

    # 计算移动平均线
    ma5 = calculate_ma(stock_data, 5)
    ma10 = calculate_ma(stock_data, 10)
    ma20 = calculate_ma(stock_data, 20)

    # 创建K线图
    kline = (
        Kline(init_opts=opts.InitOpts(width="1000px", height="500px"))
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
                title=f"{stock_name} ({stock_code}) K线图",
                subtitle="",
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
                    is_show=True,
                    type_="slider",
                    xaxis_index=[0, 1],  # 👈 控制K线图(0)和成交量图(1)
                    range_start=0,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    type_="inside",
                    xaxis_index=[0, 1],  # 👈 同时联动
                    range_start=0,
                    range_end=100,
                ),
            ],
            legend_opts=opts.LegendOpts(
                is_show=True,
                pos_top=30,
                pos_bottom=10
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

    kline.overlap(line)

    # === 创建成交量柱状图 ===
    bar = (
        Bar()
        .add_xaxis(dates)
        .add_yaxis("成交量", volumes, xaxis_index=1, yaxis_index=1, bar_width="60%",
                   label_opts=opts.LabelOpts(is_show=False), itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
                      function(params) {
                        var d = params.data;
                        if (d.close > d.open) {
                            return '#ef232a';  
                        } else {
                            return '#14b143';  
                        }
                      }
                        """
                )
            ))
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category", grid_index=1),
            yaxis_opts=opts.AxisOpts(grid_index=1, split_number=2),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    # === 用 Grid 组合K线图和成交量图 ===
    grid_chart = Grid(init_opts=opts.InitOpts(width="1400px", height="800px"))
    grid_chart.add(kline, grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="60%"))
    grid_chart.add(bar, grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", pos_top="75%", height="16%"))

    return grid_chart


def process_single_stock(stock_data, stock_name, stock_code):
    """
    处理单个股票的数据和图表生成

    Args:
        stock_data: 股票信息字典，包含 'code' 和 'name'
        stock_name: 股票名称
        stock_code: 股票代码

    Returns:
        dict: 包含股票统计信息的字典
    """

    if stock_data is None or stock_data.empty:
        print(f"❌ 获取股票 {stock_name}({stock_code}) 数据失败或数据为空")
        return None

    # 创建K线图
    chart = create_kline_chart(stock_data, stock_code, stock_name)

    return chart


def main():
    stock_pool = database.stock_pool.find_many({})
    stock_pool = pd.DataFrame(list(stock_pool))

    stock_history_data = database.stock_history_data.find_many({})
    stock_history_data = pd.DataFrame(list(stock_history_data))

    stock_filter_result = database.stock_filter_result.find_many({})
    stock_filter_result = pd.DataFrame(list(stock_filter_result))

    if stock_pool.empty or stock_history_data.empty or stock_filter_result.empty:
        print("❌ 图表生成依赖的数据为空，请先完成数据拉取和策略筛选")
        return

    stock_pool = stock_pool.drop_duplicates(subset=["股票代码"]).copy()
    stock_history_data = stock_history_data.drop_duplicates(subset=["股票代码", "交易日期"]).copy()
    stock_filter_result = stock_filter_result.drop_duplicates(subset=["股票代码"]).reset_index(drop=True)
    stock_name_map = stock_pool.set_index("股票代码")["股票名称"].to_dict()

    page = Page()

    # 创建输出目录
    output_dir = "output-chart"
    os.makedirs(output_dir, exist_ok=True)

    print("🚀 开始批量生成股票K线图")
    print(f"📊 共需处理 {len(stock_filter_result)} 只股票")
    print("=" * 60)

    # 逐个处理每只股票

    for index, row in tqdm(stock_filter_result.iterrows(), total=len(stock_filter_result), desc="正在生成股票走势图"):
        stock_code = row["股票代码"]
        stock_name = stock_name_map.get(stock_code)
        if not stock_name:
            print(f"⚠️ 股票池中缺少 {stock_code} 的名称信息，已跳过")
            continue

        stock_data = stock_history_data[stock_history_data["股票代码"] == stock_code].sort_values(by="交易日期",
                                                                                                  ascending=True).reset_index(
            drop=True)
        chart = process_single_stock(stock_data, stock_name, stock_code)
        if chart is not None:
            page.add(chart)

    # 保存图表
    output_file = "stock_result.html"
    output_path = os.path.join(output_dir, output_file)
    page.render(output_path)
    print(f"💾 K线图已保存为: {output_path}")

    # 在浏览器中打开
    abs_path = os.path.abspath(output_path)
    open_file_in_browser(abs_path)


if __name__ == "__main__":
    main()
