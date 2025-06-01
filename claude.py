import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


def get_stock_screening_strategy():
    """
    股票筛选策略：
    1. 今日成交量 >= 过去10日平均成交量的2倍
    2. 个股热度排名前500
    3. 市值 30亿-300亿
    4. 换手率 5%-20%
    5. 排除ST股、科创板、北交所
    6. 按个股热度排序
    """

    print("开始执行股票筛选策略...")

    try:
        # 1. 获取股票基本信息
        print("正在获取股票基本信息...")
        stock_info = ak.stock_info_a_code_name()

        # 2. 获取今日股票行情数据
        print("正在获取今日股票行情数据...")
        today_data = ak.stock_zh_a_spot_em()

        # 3. 获取个股人气榜(热度排名)
        print("正在获取个股热度排名...")
        hot_rank = ak.stock_hot_rank_em()

        # 4. 数据预处理
        # 排除ST股票、科创板(688开头)、北交所(430开头、830开头等)
        def filter_stocks(code):
            if pd.isna(code):
                return False
            code_str = str(code)
            # 排除科创板
            if code_str.startswith('688'):
                return False
            # 排除北交所 (430, 830, 870开头)
            if code_str.startswith(('430', '830', '870')):
                return False
            return True

        # 过滤股票代码
        today_data = today_data[today_data['代码'].apply(filter_stocks)]

        # 排除ST股票(名称包含ST)
        today_data = today_data[~today_data['名称'].str.contains('ST', na=False)]

        # 5. 筛选条件
        filtered_stocks = []

        for idx, row in today_data.iterrows():
            stock_code = row['代码']
            stock_name = row['名称']

            try:
                # 获取市值(亿元)
                market_cap = row.get('总市值', 0)
                if pd.isna(market_cap) or market_cap < 30 or market_cap > 300:
                    continue

                # 获取换手率
                turnover_rate = row.get('换手率', 0)
                if pd.isna(turnover_rate) or turnover_rate < 5 or turnover_rate > 20:
                    continue

                # 获取今日成交量
                today_volume = row.get('成交量', 0)
                if pd.isna(today_volume) or today_volume == 0:
                    continue

                # 获取历史成交量数据计算10日平均
                print(f"正在处理 {stock_code} {stock_name}...")
                hist_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                               start_date=(datetime.now() - timedelta(days=20)).strftime('%Y%m%d'),
                                               end_date=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'))

                if len(hist_data) < 10:
                    continue

                # 计算过去10日平均成交量
                avg_volume_10d = hist_data['成交量'].tail(10).mean()

                # 成交量放大条件：今日成交量 >= 过去10日平均成交量的2倍
                if today_volume < avg_volume_10d * 2:
                    continue

                # 检查热度排名
                hot_rank_data = hot_rank[hot_rank['代码'] == stock_code]
                if hot_rank_data.empty:
                    continue

                rank = hot_rank_data.iloc[0]['排名']
                if rank > 500:
                    continue

                # 符合条件的股票
                filtered_stocks.append({
                    '代码': stock_code,
                    '名称': stock_name,
                    '热度排名': rank,
                    '总市值': market_cap,
                    '换手率': turnover_rate,
                    '今日成交量': today_volume,
                    '10日平均成交量': avg_volume_10d,
                    '成交量倍数': today_volume / avg_volume_10d,
                    '涨跌幅': row.get('涨跌幅', 0),
                    '现价': row.get('最新价', 0)
                })

            except Exception as e:
                print(f"处理股票 {stock_code} 时出错: {e}")
                continue

        # 6. 结果整理和排序
        if not filtered_stocks:
            print("未找到符合条件的股票")
            return pd.DataFrame()

        result_df = pd.DataFrame(filtered_stocks)

        # 按热度排名排序
        result_df = result_df.sort_values('热度排名').reset_index(drop=True)

        print(f"\n找到 {len(result_df)} 只符合条件的股票:")
        print("=" * 80)

        # 格式化输出
        for idx, row in result_df.iterrows():
            print(f"{idx + 1:2d}. {row['代码']} {row['名称']:8s} "
                  f"热度排名:{row['热度排名']:3d} 市值:{row['总市值']:6.1f}亿 "
                  f"换手率:{row['换手率']:5.2f}% 成交量倍数:{row['成交量倍数']:5.2f} "
                  f"涨跌幅:{row['涨跌幅']:6.2f}%")

        return result_df

    except Exception as e:
        print(f"策略执行出错: {e}")
        return pd.DataFrame()


def save_results(df, filename=None):
    """保存筛选结果到Excel文件"""
    if df.empty:
        print("没有数据需要保存")
        return

    if filename is None:
        filename = f"股票筛选结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    df.to_excel(filename, index=False)
    print(f"结果已保存到: {filename}")


if __name__ == "__main__":
    # 执行策略
    result = get_stock_screening_strategy()

    # 保存结果
    if not result.empty:
        save_results(result)

        # 显示详细信息
        print("\n详细信息:")
        print(result.to_string(index=False))
    else:
        print("未找到符合条件的股票")