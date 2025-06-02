import mongodb.database as database
from filter_stock import get_filtered_stocks

"""
构建股票池数据
"""

def main():
    """主函数"""
    print("获取股票池数据...")
    try:
        stocks = get_filtered_stocks()
        print(f"成功获取 {len(stocks)} 只股票数据")
        # 先清除数据集里的老数据，再插入新获取的数据
        database.stock_pool.delete_many({})
        database.stock_pool.insert_many(stocks)
        print("已存入MongoDB")
    except Exception as e:
        print(f"获取股票数据失败: {e}")


if __name__ == "__main__":
    main()
