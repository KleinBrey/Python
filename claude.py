import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings

warnings.filterwarnings('ignore')


class StockScreeningStrategy:
    def __init__(self):
        """初始化股票筛选策略"""
        self.today = datetime.now().strftime('%Y%m%d')
        self.stock_data = None
        self.filtered_stocks = None

    def get_stock_list(self):
        """获取A股股票列表，排除ST、科创板、北交所"""
        try:
            # 获取A股实时数据
            print("正在获取A股实时数据...")
            stock_list = ak.stock_zh_a_spot_em()

            print(stock_list)

            # 过滤条件：排除ST股票、科创板(688开头)、北交所(430开头)
            filtered_list = stock_list[
                (~stock_list['名称'].str.contains('ST|*ST', na=False)) &  # 排除ST股票
                (~stock_list['代码'].str.startswith('688')) &  # 排除科创板
                (~stock_list['代码'].str.startswith('430'))  # 排除北交所
                ].copy()

            print(f"获取到 {len(filtered_list)} 只符合条件的股票")
            return filtered_list

        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None

    def get_stock_hist_data(self, symbol, days=11):
        """获取个股历史数据"""
        try:
            # 计算起始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)  # 多取一些天数以确保有足够的交易日

            hist_data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                adjust=""
            )

            if hist_data is not None and len(hist_data) > 0:
                # 确保数据按日期排序
                hist_data = hist_data.sort_values('日期').tail(days)
                return hist_data
            return None

        except Exception as e:
            print(f"获取 {symbol} 历史数据失败: {e}")
            return None

    def calculate_volume_ratio(self, hist_data):
        """计算今日成交量与过去10日平均成交量的比值"""
        if hist_data is None or len(hist_data) < 2:
            return None

        try:
            # 最新一天的成交量（今日）
            today_volume = hist_data.iloc[-1]['成交量']

            # 过去10天的平均成交量（不包括今日）
            if len(hist_data) >= 11:
                past_10_days = hist_data.iloc[-11:-1]['成交量'].mean()
            else:
                past_10_days = hist_data.iloc[:-1]['成交量'].mean()

            if past_10_days > 0:
                volume_ratio = today_volume / past_10_days
                return volume_ratio
            return None

        except Exception as e:
            print(f"计算成交量比值失败: {e}")
            return None

    def get_stock_hot_rank(self):
        """获取个股热度排名数据"""
        try:
            print("正在获取个股热度排名...")
            # 使用东财的热度排名数据
            hot_rank = ak.stock_hot_rank_em()
            return hot_rank
        except Exception as e:
            print(f"获取热度排名失败: {e}")
            return None

    def screen_stocks(self):
        """执行股票筛选策略"""
        print("开始执行股票筛选策略...")

        # 1. 获取股票列表
        stock_list = self.get_stock_list()
        if stock_list is None:
            return None

        # 2. 获取个股热度排名
        hot_rank = self.get_stock_hot_rank()
        if hot_rank is not None:
            # 筛选热度排名前500的股票
            hot_stocks = hot_rank.head(500)['代码'].tolist()
            stock_list = stock_list[stock_list['代码'].isin(hot_stocks)]
            print(f"筛选热度前500后剩余: {len(stock_list)} 只股票")

        # 3. 基本筛选条件
        print("应用基本筛选条件...")
        stock_list = stock_list[
            (stock_list['总市值'] >= 30e8) &  # 市值大于30亿
            (stock_list['总市值'] <= 300e8) &  # 市值小于300亿
            (stock_list['换手率'] >= 5) &  # 换手率大于5%
            (stock_list['换手率'] <= 20)  # 换手率小于20%
            ].copy()

        print(f"基本筛选后剩余: {len(stock_list)} 只股票")

        # 4. 计算成交量比值
        print("计算成交量比值...")
        results = []

        for idx, row in stock_list.iterrows():
            symbol = row['代码']
            print(f"处理股票: {symbol} - {row['名称']} ({idx + 1}/{len(stock_list)})")

            # 获取历史数据
            hist_data = self.get_stock_hist_data(symbol)
            if hist_data is None:
                continue

            # 计算成交量比值
            volume_ratio = self.calculate_volume_ratio(hist_data)
            if volume_ratio is None or volume_ratio < 2.0:  # 成交量比值需要>=2倍
                continue

            # 添加到结果
            result_row = {
                '代码': symbol,
                '名称': row['名称'],
                '最新价': row['最新价'],
                '涨跌幅': row['涨跌幅'],
                '换手率': row['换手率'],
                '成交量': row['成交量'],
                '成交额': row['成交额'],
                '总市值': row['总市值'],
                '流通市值': row['流通市值'],
                '成交量比值': round(volume_ratio, 2),
                '个股热度排名': hot_rank[hot_rank['代码'] == symbol].index[0] + 1 if hot_rank is not None and symbol in
                                                                                     hot_rank['代码'].values else 999
            }
            results.append(result_row)

            # 避免请求过快
            time.sleep(0.1)

        if not results:
            print("没有找到符合条件的股票")
            return None

        # 5. 创建结果DataFrame并按热度排序
        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values('个股热度排名').reset_index(drop=True)

        print(f"筛选完成，共找到 {len(result_df)} 只符合条件的股票")
        self.filtered_stocks = result_df
        return result_df

    def export_to_excel(self, filename=None):
        """导出结果到Excel"""
        if self.filtered_stocks is None:
            print("没有数据可以导出")
            return False

        if filename is None:
            filename = f"股票筛选结果_{self.today}.xlsx"

        try:
            # 格式化数据
            export_data = self.filtered_stocks.copy()

            # 格式化数值列
            export_data['总市值'] = (export_data['总市值'] / 1e8).round(2).astype(str) + '亿'
            export_data['流通市值'] = (export_data['流通市值'] / 1e8).round(2).astype(str) + '亿'
            export_data['成交额'] = (export_data['成交额'] / 1e8).round(2).astype(str) + '亿'
            export_data['换手率'] = export_data['换手率'].astype(str) + '%'
            export_data['涨跌幅'] = export_data['涨跌幅'].astype(str) + '%'

            # 导出到Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                export_data.to_excel(writer, sheet_name='筛选结果', index=False)

                # 获取工作表并调整列宽
                worksheet = writer.sheets['筛选结果']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 20)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            print(f"结果已导出到: {filename}")
            return True

        except Exception as e:
            print(f"导出Excel失败: {e}")
            return False

    def display_results(self):
        """显示筛选结果"""
        if self.filtered_stocks is None:
            print("没有筛选结果")
            return

        print("\n" + "=" * 80)
        print("股票筛选结果汇总")
        print("=" * 80)
        print(f"筛选日期: {self.today}")
        print(f"符合条件股票数量: {len(self.filtered_stocks)}")
        print("\n筛选条件:")
        print("1. 今日成交量 >= 过去10日平均成交量的2倍")
        print("2. 个股热度排名前500")
        print("3. 市值: 30亿 ~ 300亿")
        print("4. 换手率: 5% ~ 20%")
        print("5. 排除ST股票、科创板、北交所")
        print("\n" + "-" * 80)

        # 显示前20只股票
        display_df = self.filtered_stocks.head(20).copy()

        # 格式化显示
        display_df['总市值_显示'] = (display_df['总市值'] / 1e8).round(1).astype(str) + '亿'
        display_df['成交量比值_显示'] = display_df['成交量比值'].astype(str) + '倍'

        print(display_df[['代码', '名称', '最新价', '涨跌幅', '换手率', '总市值_显示', '成交量比值_显示',
                          '个股热度排名']].to_string(index=False))

        if len(self.filtered_stocks) > 20:
            print(f"\n... 还有 {len(self.filtered_stocks) - 20} 只股票，详见Excel文件")


def main():
    """主函数"""
    print("=" * 60)
    print("股票筛选策略 - 基于成交量和热度")
    print("=" * 60)

    # 创建策略实例
    strategy = StockScreeningStrategy()

    # 执行筛选
    results = strategy.screen_stocks()

    if results is not None:
        # 显示结果
        strategy.display_results()

        # 导出Excel
        strategy.export_to_excel()
    else:
        print("筛选失败，请检查网络连接和数据源")


if __name__ == "__main__":
    main()