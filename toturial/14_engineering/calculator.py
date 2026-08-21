"""供测试章节使用的最小生产模块；直接运行也可查看示例。"""

def add(left: float, right: float) -> float:
    """返回两数之和。"""
    return left + right


def percentage_change(old: float, new: float) -> float:
    """计算涨跌幅，旧值必须大于 0。"""
    if old <= 0:
        raise ValueError("old 必须大于 0")
    return (new - old) / old


if __name__ == "__main__":
    print(add(1, 2))
    print(f"涨跌幅：{percentage_change(100, 105):.2%}")
