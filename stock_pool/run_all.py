
import sys
from filtered_stock_pool import main as pool_main
from stock_data_collector import main as daily_main


def run():
    print("\n============================")
    print("Step 1: 生成股票池")
    print("============================")
    try:
        pool_main()
    except Exception as e:
        print(f"❌ 股票池生成失败: {e}")
        sys.exit(1)

    print("\n============================")
    print("Step 2: 拉取股票历史数据")
    print("============================")
    try:
        daily_main()
    except Exception as e:
        print(f"❌ 股票历史数据拉取失败: {e}")
        sys.exit(1)

    print("\n✅ 全流程执行完成！")


if __name__ == "__main__":
    run()
