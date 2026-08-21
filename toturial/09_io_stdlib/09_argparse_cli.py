"""
==================================================
知识点：argparse 命令行参数
==================================================

试运行：python 09_argparse_cli.py 600519 --mode weekly --limit 3 --verbose
"""

import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="模拟查询股票行情")
    parser.add_argument("symbol", nargs="?", default="600519", help="位置参数：股票代码")
    parser.add_argument(
        "--mode",
        choices=["daily", "weekly"],
        default="daily",
        help="可选参数：周期，只允许 choices 中的值",
    )
    parser.add_argument("--limit", type=int, default=5, help="返回条数（默认 5）")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="出现该开关时值为 True，不需要再写 true",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(f"symbol={args.symbol} mode={args.mode} limit={args.limit}")
    if args.verbose:
        print("已开启详细输出")


if __name__ == "__main__":
    main()

"""
练习：增加 --format 参数，只允许 json/csv，默认 json。

# ==========================
# 参考答案
# ==========================
# parser.add_argument("--format", choices=["json", "csv"], default="json")

本节总结：位置参数通常必需；-- 开头是可选参数；type/choices 负责基础校验。
"""
