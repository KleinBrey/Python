#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票数据获取与导出工具
使用AKShare获取A股所有股票的详细指标数据，包括过去十日的成交量、换手率等
"""

import time
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from utils import convert_data


class StockDataCollector:
    """A股股票数据收集器"""

    def __init__(self):
        self.all_stocks_data = []
        self.failed_stocks = []

    def get_historical_data(self, stock_code, period="daily", start_date=None, end_date=None):
        """
        获取单只股票的历史数据

        参数:
        stock_code: 股票代码
        period: 数据周期，默认为日线
        start_date: 开始日期
        end_date: 结束日期
        """
        try:
            # 使用东财数据源获取历史行情数据
            df = ak.stock_zh_a_hist(symbol=stock_code,
                                    period=period,
                                    start_date=start_date,
                                    end_date=end_date,
                                    adjust="qfq")  # 前复权
            return df
        except Exception as e:
            print(f"获取股票 {stock_code} 历史数据失败: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, df):
        """计算技术指标"""
        if df.empty:
            return {}

        try:
            # 基础统计
            latest_data = df.iloc[-1]
            recent_10_days = df.tail(10)

            indicators = {
                '最新价格': latest_data['收盘'],
                '最新成交量': latest_data['成交量'],
                '最新换手率': latest_data.get('换手率', 0),
                '最新成交额': latest_data['成交额'],

                # 过去10日统计
                '10日平均成交量': recent_10_days['成交量'].mean(),
                '10日成交量总和': recent_10_days['成交量'].sum(),
                '10日最大成交量': recent_10_days['成交量'].max(),
                '10日最小成交量': recent_10_days['成交量'].min(),

                '10日平均换手率': recent_10_days.get('换手率', pd.Series([0] * len(recent_10_days))).mean(),
                '10日最大换手率': recent_10_days.get('换手率', pd.Series([0] * len(recent_10_days))).max(),
                '10日最小换手率': recent_10_days.get('换手率', pd.Series([0] * len(recent_10_days))).min(),

                '10日平均成交额': recent_10_days['成交额'].mean(),
                '10日成交额总和': recent_10_days['成交额'].sum(),

                # 价格指标
                '10日最高价': recent_10_days['最高'].max(),
                '10日最低价': recent_10_days['最低'].min(),
                '10日平均收盘价': recent_10_days['收盘'].mean(),
                '10日价格振幅': (recent_10_days['最高'].max() - recent_10_days['最低'].min()) / recent_10_days[
                    '收盘'].mean() * 100,

                # 涨跌统计
                '10日涨跌幅': (latest_data['收盘'] - recent_10_days.iloc[0]['收盘']) / recent_10_days.iloc[0][
                    '收盘'] * 100,
                '10日上涨天数': len(recent_10_days[recent_10_days['涨跌幅'] > 0]),
                '10日下跌天数': len(recent_10_days[recent_10_days['涨跌幅'] < 0]),
            }

            return indicators

        except Exception as e:
            print(f"计算技术指标失败: {e}")
            return {}

    def get_stock_detailed_info(self, stock_code):
        """获取股票详细信息"""
        try:
            # 获取个股信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                info_dict = dict(zip(stock_info['item'], stock_info['value']))
                return {
                    '总市值': info_dict.get('总市值', 0),
                    '流通市值': info_dict.get('流通市值', 0),
                    '市盈率': info_dict.get('市盈率-动态', 0),
                    '市净率': info_dict.get('市净率', 0),
                    '股息率': info_dict.get('股息率', 0),
                }
        except:
            pass
        return {}

    def collect_single_stock_data(self, stock_code, stock_name):
        """收集单只股票的完整数据"""
        print(f"正在处理股票: {stock_code} - {stock_name}")

        # 计算日期范围（过去15个交易日，确保有足够数据）
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=20)).strftime('%Y%m%d')

        # 获取历史数据
        hist_data = self.get_historical_data(stock_code, start_date=start_date, end_date=end_date)

        if hist_data.empty:
            self.failed_stocks.append(f"{stock_code}-{stock_name}")
            return None

        # 计算技术指标
        technical_indicators = self.calculate_technical_indicators(hist_data)

        # 获取详细信息
        detailed_info = self.get_stock_detailed_info(stock_code)

        # 合并所有数据
        stock_data = {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '数据更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **technical_indicators,
            **detailed_info
        }

        # 添加每日详细数据（过去10日）
        if len(hist_data) >= 10:
            recent_data = hist_data.tail(10)
            for i, (_, row) in enumerate(recent_data.iterrows(), 1):
                stock_data[f'第{i}日_日期'] = row['日期']
                stock_data[f'第{i}日_收盘价'] = row['收盘']
                stock_data[f'第{i}日_成交量'] = row['成交量']
                stock_data[f'第{i}日_成交额'] = row['成交额']
                stock_data[f'第{i}日_换手率'] = row.get('换手率', 0)
                stock_data[f'第{i}日_涨跌幅'] = row['涨跌幅']

        return stock_data

    def collect_all_stocks_data(self, stock_list, delay=0.1):
        """
        收集所有股票数据

        参数:
        delay: 每次请求间的延迟时间（秒）
        """
        # 获取股票列表
        if stock_list.empty:
            print("无法获取股票列表，程序退出")
            return

        total_stocks = len(stock_list)
        print(f"开始处理 {total_stocks} 只股票...")

        for idx, (_, row) in enumerate(stock_list.iterrows(), 1):
            stock_code = row['代码']
            stock_name = row['名称']

            print(f"进度: {idx}/{total_stocks} ({idx / total_stocks * 100:.1f}%)")

            # 收集单只股票数据
            stock_data = self.collect_single_stock_data(stock_code, stock_name)

            if stock_data:
                self.all_stocks_data.append(stock_data)

            # 添加延迟，避免请求过于频繁
            if delay > 0:
                time.sleep(delay)

            # 每处理100只股票输出一次进度
            if idx % 100 == 0:
                print(f"已完成 {idx} 只股票，成功 {len(self.all_stocks_data)} 只，失败 {len(self.failed_stocks)} 只")

        print(f"\n数据收集完成！")
        print(f"总计: {total_stocks} 只股票")
        print(f"成功: {len(self.all_stocks_data)} 只股票")
        print(f"失败: {len(self.failed_stocks)} 只股票")

        if self.failed_stocks:
            print("失败的股票:", ', '.join(self.failed_stocks[:10]))  # 只显示前10个


def collect_stock_all_data(stocks):
    """主函数"""
    print("=" * 60)
    print("A股股票数据收集工具")
    print("=" * 60)
    # 创建数据收集器
    collector = StockDataCollector()

    try:
        collector.collect_all_stocks_data(stocks, delay=0.1)
        # 导出数据
        if collector.all_stocks_data:
            print("\n程序执行完成！")
            cleaned_data = convert_data.to_mongo_format(collector.all_stocks_data)
            return cleaned_data

        else:
            print("\n没有成功获取任何数据")

    except Exception as e:
        print(f"\n程序执行出错: {e}")



