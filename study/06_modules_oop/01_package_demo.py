"""
==================================================
知识点：导入自己编写的包
==================================================

本文件与 example_package 位于同一目录，因此直接运行时可以导入它。
"""

from example_package import calculate_change
from example_package.calculations import calculate_change as direct_calculate_change

print(f"从包公开入口导入：{calculate_change(10, 11):.2%}")
print(f"从具体模块导入：{direct_calculate_change(20, 21):.2%}")

# 相对导入（from .calculations import ...）主要在包内部使用。
# 应用入口通常用绝对导入，更容易看出名称来自哪里。

"""
本节总结：包通过目录组织模块；__init__.py 可定义友好的公共导入入口。
"""
