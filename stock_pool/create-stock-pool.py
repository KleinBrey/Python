from mongodb import database
from stock_pool.filter_stock import get_filtered_stocks
from stock_pool.require_detail import collect_stock_all_data

"""
构建股票池数据
"""

def main():
    """主函数"""
    print("获取股票池数据...")
    try:
        stocks = get_filtered_stocks()
        stocks = collect_stock_all_data(stocks)
        # 先清除数据集里的老数据，再插入新获取的数据
        database.stock_pool.delete_many({})
        database.stock_pool.insert_many(stocks)
        print("已存入MongoDB")
    except Exception as e:
        print(f"获取股票数据失败: {e}")


if __name__ == "__main__":
    main()
