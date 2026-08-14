"""
==================================================
知识点：try、except、else、finally 与常见异常
==================================================
"""

def parse_price(raw: str) -> float | None:
    try:
        price = float(raw)
    except ValueError as error:
        print("ValueError：文本不能转换为数字：", error)
        return None
    else:
        # else 只在 try 没有异常时运行；将成功逻辑放这里可缩小 try 范围。
        print("解析成功")
        return price
    finally:
        # finally 无论成功、失败甚至 return 都执行，常用于释放资源。
        print("解析流程结束")


print(parse_price("10.5"))
print(parse_price("未知"))

# 常见异常：
# TypeError：操作类型不合适，如 1 + "2"
# KeyError：字典缺少键；IndexError：序列下标越界
# FileNotFoundError：文件不存在；ValueError：类型对但值不合法

data = {"symbol": "600519"}
try:
    print(data["price"])
except KeyError as error:
    print("缺少字段：", error)

# ⚠️ 不要写 except Exception: pass，它会悄悄吞掉问题。

"""
本节总结：只捕获能处理的具体异常；else 放成功分支；finally 负责必要清理。
"""
