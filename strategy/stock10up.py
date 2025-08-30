
"""
股票筛选策略
筛选条件：
1. 今日成交量为过去十日平均成交量的2倍及以上
2. 市值大于30亿小于300亿
3. 换手率大于5%小于20%
4. ST股除外，科创板除外，北交所除外
5. 按当天个股热度进行排序，导出excel
"""

import time
import warnings
from datetime import datetime, timedelta
import numpy as np
import akshare as ak
import pandas as pd

import mongodb.database as database

warnings.filterwarnings('ignore')


class StockScreener:
    def __init__(self):
        self.today = datetime.now().strftime('%Y%m%d')
        self.results = pd.DataFrame()


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

    def export_to_mongodb(self, df):
        """导出结果到MongoDB"""
        if df.empty:
            print("没有数据可导出")
            return

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

        # 转换DataFrame为字典列表
        records = export_df.to_dict('records')

        # 为每条记录添加时间戳和筛选日期
        current_time = datetime.now()
        for record in records:
            record['筛选日期'] = self.today
            record['创建时间'] = current_time
            record['数据来源'] = 'akshare'

            # 处理NaN值，MongoDB不支持NaN
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, (np.int64, np.float64)):
                    record[key] = float(value) if not np.isnan(value) else None

        # 批量插入数据
        if records:
            # 可以选择是否先清空当天的数据
            # collection.delete_many({"筛选日期": self.today})  # 取消注释以删除当天旧数据
            result = database.stock_filter_result.insert_many(records)
            print(f"成功导入MongoDB:")
            print(f"  插入记录数: {len(result.inserted_ids)}")
            print(f"  筛选日期: {self.today}")

            # 创建索引以提高查询性能
            try:
                database.stock_filter_result.create_index([("代码", 1), ("筛选日期", -1)])
                database.stock_filter_result.create_index([("热度指标", -1)])
                database.stock_filter_result.create_index([("筛选日期", -1)])
            except Exception as idx_e:
                print(f"创建索引时出现警告: {idx_e}")

    def run_screening(self,stocks):
        """执行完整的股票筛选流程"""
        print("=" * 50)
        print("开始执行股票筛选策略")
        print("=" * 50)

        # 4. 按换手率筛选
        filtered_stocks = self.filter_by_turnover_rate(stocks)
        if filtered_stocks.empty:
            print("换手率筛选后无结果")
            return

        # 5. 按成交量放大筛选（最耗时的步骤）
        filtered_stocks = self.filter_by_volume_surge(filtered_stocks)
        if filtered_stocks.empty:
            print("成交量筛选后无结果")
            return


        # 7. 导出Excel
        self.export_to_mongodb(filtered_stocks)

        # 8. 显示结果摘要
        print("\n" + "=" * 50)
        print("筛选完成！结果摘要：")
        print("=" * 50)
        if not filtered_stocks.empty:
            print(filtered_stocks[['代码', '名称', '最新价', '涨跌幅', '换手率',
                                 '总市值_亿', '成交量放大倍数', '热度指标']].head(10))

        return filtered_stocks


def getFilteredStocks(stocks):
    screener = StockScreener()
    results = screener.run_screening(stocks)
    return results


