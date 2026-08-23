import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.traceback import install

install(show_locals=True)

console = Console()


def print_header() -> None:
    console.print(
        Panel(
            "[bold cyan]A 股量化数据管理系统[/bold cyan]",
            title="[bold]Stock Quant[/bold]",
            border_style="cyan",
            padding=(1, 10),
        )
    )


def print_database_status() -> None:
    console.print("\n[bold]数据库[/bold]")
    console.print("[green]✓ DuckDB 初始化完成[/green]")


def print_task(title: str) -> None:
    console.print("\n[bold]任务[/bold]")
    console.print(title)


def fetch_daily_bar(symbol: str) -> str:
    """
    模拟请求股票日线。

    实际使用时，把这里替换成：
    self.tushare_provider.fetch_historical(...)
    """

    time.sleep(random.uniform(0.1, 0.5))

    # 模拟少量失败
    if random.random() < 0.03:
        raise RuntimeError("API 请求失败")

    return symbol


def print_statistics(
    success_count: int,
    failed_symbols: list[str],
    total: int,
) -> None:

    console.print("\n[bold]统计[/bold]\n")

    table = Table(show_header=True)

    table.add_column("项目", style="bold")
    table.add_column("数量", justify="right")

    table.add_row(
        "[green]成功[/green]",
        str(success_count),
    )

    table.add_row(
        "[red]失败[/red]",
        str(len(failed_symbols)),
    )

    table.add_row(
        "总计",
        str(total),
    )

    console.print(table)


def print_failed_symbols(
    failed_symbols: list[str],
) -> None:

    if not failed_symbols:
        return

    console.print("\n[yellow]⚠ 失败股票：[/yellow]")

    for symbol in failed_symbols:
        console.print(f"[red]{symbol}[/red]")


def update_daily_bar() -> None:

    symbols = [
        "600519.SH",
        "601899.SH",
        "601888.SH",
        "600036.SH",
        "000001.SZ",
        "000858.SZ",
        "002594.SZ",
        "300750.SZ",
        "601318.SH",
        "600900.SH",
        "002415.SZ",
        "600276.SH",
        "601012.SH",
        "000333.SZ",
        "600030.SH",
    ]

    total = len(symbols)

    success_count = 0
    failed_symbols = []

    print_task("更新股票日线")

    progress = Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(
            bar_width=30,
        ),
        TaskProgressColumn(),
        TextColumn("[bold]{task.completed:.0f}/{task.total:.0f}[/bold]"),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:

        task_id = progress.add_task(
            "同步股票",
            total=total,
        )

        with ThreadPoolExecutor(
            max_workers=5,
            thread_name_prefix="daily-bar",
        ) as executor:

            futures = {
                executor.submit(
                    fetch_daily_bar,
                    symbol,
                ): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):

                symbol = futures[future]

                try:
                    future.result()

                    success_count += 1

                except Exception:
                    failed_symbols.append(symbol)

                progress.update(
                    task_id,
                    description=f"同步股票 [dim]{symbol}[/dim]",
                )

                progress.advance(task_id)

    print_statistics(
        success_count,
        failed_symbols,
        total,
    )

    print_failed_symbols(failed_symbols)

    console.print("\n[bold green]✓ 股票日线同步完成[/bold green]")


def main() -> None:

    print_header()

    print_database_status()

    update_daily_bar()


if __name__ == "__main__":
    main()
