#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选策略
筛选条件：
1. 今日成交量为过去十日平均成交量的2倍及以上
2. 市值大于30亿小于300亿
3. 换手率大于5%小于20%
4. ST股除外，科创板除外，北交所除外
5. 按当天个股热度进行排序，导出excel
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import time

warnings.filterwarnings('ignore')


class StockScreener:
    def __init__(self):
        self.today = datetime.now().strftime('%Y%m%d')
        self.results = pd.DataFrame()

    def get_all_stocks_data(self):
        """获取所有A股实时数据"""
        print("正在获取所有A股实时数据...")
        try:
            # 获取A股实时行情数据（东财）- 包含市值、换手率等信息
            stock_data = ak.stock_zh_a_spot_em()
            print(f"成功获取 {len(stock_data)} 只股票的实时数据")
            return stock_data
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return pd.DataFrame()

    def filter_by_stock_type(self, df):
        """过滤股票类型：排除ST股、科创板、北交所"""
        print("正在过滤股票类型...")
        initial_count = len(df)

        # 排除ST股票（名称包含ST、*ST、S*ST等）
        df = df[~df['名称'].str.contains('ST|退', na=False)]

        # 排除科创板（股票代码688开头）
        df = df[~df['代码'].str.startswith('688')]

        # 排除北交所（股票代码以43、83、87开头）
        df = df[~df['代码'].str.startswith(('43', '83', '87'))]

        # 排除创业板中的特殊股票
        df = df[~df['代码'].str.startswith('30')]  # 可选：如果不想要创业板

        filtered_count = len(df)
        print(f"股票类型过滤完成，从 {initial_count} 只股票筛选到 {filtered_count} 只股票")
        return df

    def filter_by_market_cap(self, df):
        """按市值筛选：30亿 < 市值 < 300亿"""
        print("正在按市值筛选...")
        initial_count = len(df)

        # 总市值单位通常是元，需要转换为亿元
        df['总市值_亿'] = df['总市值'] / 100000000

        # 筛选市值在30亿到300亿之间
        df = df[(df['总市值_亿'] > 30) & (df['总市值_亿'] < 300)]

        filtered_count = len(df)
        print(f"市值筛选完成，从 {initial_count} 只股票筛选到 {filtered_count} 只股票")
        return df

    def filter_by_turnover_rate(self, df):
        """按换手率筛选：5% < 换手率 < 20%"""
        print("正在按换手率筛选...")
        initial_count = len(df)

        # 筛选换手率在5%到20%之间
        df = df[(df['换手率'] > 5) & (df['换手率'] < 20)]

        filtered_count = len(df)
        print(f"换手率筛选完成，从 {initial_count} 只股票筛选到 {filtered_count} 只股票")
        return df

    def get_historical_volume(self, stock_code, days=10):
        """获取个股历史成交量数据"""
        try:
            # 获取历史行情数据
            hist_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                           start_date=(datetime.now() - timedelta(days=20)).strftime('%Y%m%d'),
                                           end_date=self.today, adjust="")

            if len(hist_data) >= days + 1:  # 至少需要11天数据（10天历史+1天今日）
                # 计算过去10天的平均成交量（排除今日）
                avg_volume = hist_data['成交量'].iloc[:-1].tail(days).mean()
                today_volume = hist_data['成交量'].iloc[-1]
                return avg_volume, today_volume
            else:
                return None, None
        except Exception as e:
            print(f"获取 {stock_code} 历史数据失败: {e}")
            return None, None

    def filter_by_volume_surge(self, df):
        """按成交量放大筛选：今日成交量 >= 过去10日平均成交量的2倍"""
        print("正在按成交量放大筛选...")
        initial_count = len(df)

        volume_ratio_list = []
        filtered_stocks = []

        for idx, row in df.iterrows():
            stock_code = row['代码']
            print(f"处理股票 {stock_code} ({row['名称']})...")

            avg_volume, today_volume = self.get_historical_volume(stock_code)

            if avg_volume is not None and today_volume is not None and avg_volume > 0:
                volume_ratio = today_volume / avg_volume
                if volume_ratio >= 2.0:  # 成交量放大2倍以上
                    volume_ratio_list.append(volume_ratio)
                    filtered_stocks.append(row)
                    print(f"  ✓ 符合条件，成交量放大 {volume_ratio:.2f} 倍")
                else:
                    print(f"  ✗ 不符合条件，成交量放大 {volume_ratio:.2f} 倍")
            else:
                print(f"  ✗ 无法获取历史数据")

            # 添加延时避免请求过快
            time.sleep(0.1)

        if filtered_stocks:
            result_df = pd.DataFrame(filtered_stocks)
            result_df['成交量放大倍数'] = volume_ratio_list

            filtered_count = len(result_df)
            print(f"成交量筛选完成，从 {initial_count} 只股票筛选到 {filtered_count} 只股票")
            return result_df
        else:
            print("没有股票符合成交量放大条件")
            return pd.DataFrame()

    def sort_by_popularity(self, df):
        """按热度排序（使用换手率 * 成交量放大倍数作为热度指标）"""
        if df.empty:
            return df

        print("正在按热度排序...")

        # 计算热度指标：换手率 * 成交量放大倍数 * 涨跌幅
        df['热度指标'] = df['换手率'] * df['成交量放大倍数'] * (1 + df['涨跌幅'].abs() / 100)

        # 按热度指标降序排列
        df = df.sort_values('热度指标', ascending=False)

        print(f"热度排序完成")
        return df

    def export_to_excel(self, df, filename=None):
        """导出结果到Excel"""
        if df.empty:
            print("没有数据可导出")
            return

        if filename is None:
            filename = f"股票筛选结果_{self.today}.xlsx"

        # 选择要导出的列
        export_columns = [
            '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额',
            '换手率', '总市值_亿', '流通市值', '成交量放大倍数', '热度指标'
        ]

        # 只选择存在的列
        available_columns = [col for col in export_columns if col in df.columns]
        export_df = df[available_columns].copy()

        # 格式化数据
        export_df['总市值_亿'] = export_df['总市值_亿'].round(2)
        export_df['成交量放大倍数'] = export_df['成交量放大倍数'].round(2)
        export_df['热度指标'] = export_df['热度指标'].round(2)

        try:
            export_df.to_excel(filename, index=False, engine='openpyxl')
            print(f"结果已导出到: {filename}")
            print(f"共导出 {len(export_df)} 只股票")
        except Exception as e:
            print(f"导出Excel失败: {e}")

    def run_screening(self):
        """执行完整的股票筛选流程"""
        print("=" * 50)
        print("开始执行股票筛选策略")
        print("=" * 50)

        # 1. 获取所有股票数据
        all_stocks = self.get_all_stocks_data()
        if all_stocks.empty:
            print("无法获取股票数据，程序退出")
            return

        # 2. 按股票类型筛选
        filtered_stocks = self.filter_by_stock_type(all_stocks)
        if filtered_stocks.empty:
            print("股票类型筛选后无结果")
            return

        # 3. 按市值筛选
        filtered_stocks = self.filter_by_market_cap(filtered_stocks)
        if filtered_stocks.empty:
            print("市值筛选后无结果")
            return

        # 4. 按换手率筛选
        filtered_stocks = self.filter_by_turnover_rate(filtered_stocks)
        if filtered_stocks.empty:
            print("换手率筛选后无结果")
            return

        # 5. 按成交量放大筛选（最耗时的步骤）
        filtered_stocks = self.filter_by_volume_surge(filtered_stocks)
        if filtered_stocks.empty:
            print("成交量筛选后无结果")
            return

        # 6. 按热度排序
        final_results = self.sort_by_popularity(filtered_stocks)

        # 7. 导出Excel
        self.export_to_excel(final_results)

        # 8. 显示结果摘要
        print("\n" + "=" * 50)
        print("筛选完成！结果摘要：")
        print("=" * 50)
        if not final_results.empty:
            print(final_results[['代码', '名称', '最新价', '涨跌幅', '换手率',
                                 '总市值_亿', '成交量放大倍数', '热度指标']].head(10))

        return final_results


def main():
    """主函数"""
    screener = StockScreener()
    results = screener.run_screening()
    return results


if __name__ == "__main__":
    # 运行筛选策略
    results = main()