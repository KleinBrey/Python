"""
==================================================
知识点：pytest、assert 与测试命名
==================================================

运行：python -m pytest study/14_engineering/test_calculator.py -v
也可 python test_calculator.py 做最小自检。
"""

from calculator import add, percentage_change

def test_add() -> None:
    # assert 表达“预期必须为真”；失败时 pytest 会展示实际值和预期差异。
    assert add(1, 2) == 3


def test_percentage_change() -> None:
    assert percentage_change(100, 110) == 0.1


if __name__ == "__main__":
    test_add()
    test_percentage_change()
    print("基础测试通过")

# pytest 默认发现 test_*.py / *_test.py 和 test_* 函数。
# 每个测试应独立、快速、结果稳定；失败测试也是需求和回归保护。

"""
本节总结：测试把预期写成可重复执行的代码；文件和函数遵循 test_ 命名。
"""
