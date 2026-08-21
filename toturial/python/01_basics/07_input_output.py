"""
==================================================
知识点：input 与格式化输出
==================================================

直接运行时可输入内容；加 --demo 可无交互演示，便于自动检查：
python 07_input_output.py --demo
"""

import sys

if "--demo" in sys.argv:
    name, raw_quantity = "小林", "100"
else:
    # input() 返回的一定是 str，即使用户键入 100 也是字符串。
    name = input("请输入姓名：").strip()
    raw_quantity = input("请输入买入数量：").strip()

try:
    quantity = int(raw_quantity)
except ValueError:
    print("数量必须是整数，本次使用默认值 0")
    quantity = 0

print(f"{name or '匿名用户'} 计划买入 {quantity:,} 股")
print("数量：{}，状态：{}".format(quantity, "有效" if quantity > 0 else "无效"))

print("A{} B{}".format(1,2))

"""
练习：读取单价和数量，打印保留两位小数的总价。

# ==========================
# 参考答案（思路）
# ==========================
# price = float(input("单价："))
# quantity = int(input("数量："))
# print(f"总价：{price * quantity:.2f}")

本节总结：input 永远返回 str；转换外部输入时要处理错误；f-string 最直观。
"""
