import sys

try:
    from stock_cache.filtered_stock_pool import main as pool_main
    from stock_cache.stock_data_collector import main as daily_main
except ModuleNotFoundError:
    from filtered_stock_pool import main as pool_main
    from stock_data_collector import main as daily_main


def run_step(title: str, func) -> None:
    print("\n============================")
    print(title)
    print("============================")
    try:
        func()
    except Exception as exc:
        print(f"❌ {title}失败: {exc}")
        sys.exit(1)


def run():
    run_step("Step 1: 生成股票池", pool_main)
    run_step("Step 2: 拉取股票历史数据", daily_main)

    print("\n✅ 全流程执行完成！")


if __name__ == "__main__":
    run()
