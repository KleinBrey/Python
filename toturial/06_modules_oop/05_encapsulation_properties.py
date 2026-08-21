"""
==================================================
知识点：封装、_name、__name 与 property
==================================================
"""

class Position:
    def __init__(self, symbol: str, quantity: int):
        self.symbol = symbol
        self._quantity = 0  # 单下划线表示“内部使用”，是约定而非强制权限
        self.__audit_code = "internal"  # 双下划线会名称改写，主要避免子类意外冲突
        self.quantity = quantity  # 走 setter，复用校验

    @property
    def quantity(self) -> int:
        """getter 让调用者像读属性一样使用，同时保留内部控制。"""
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if value < 0:
            raise ValueError("持仓数量不能为负数")
        self._quantity = value


position = Position("600519", 100)
print(position.quantity)  # 看起来是属性，实际调用 getter
position.quantity = 200   # 看起来是赋值，实际调用 setter
print(position.quantity)

# Python 强调“大家自觉遵守接口”，不是绝对私有。无需验证时直接公开属性更 Pythonic。
# 错误示例：position.quantity = -1  # ValueError

"""
本节总结：_name 表示内部实现；property 在保持属性语法的同时加入校验或计算。
"""
