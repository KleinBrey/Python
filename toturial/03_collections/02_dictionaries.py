"""
==================================================
知识点：字典 Dictionary
==================================================

dict 保存“键 -> 值”的映射，约等于常见用途下的 JavaScript Object。
Python 3.7+ 明确保留插入顺序，但选择 dict 的核心理由仍是按键快速查找。
"""

user = {"name": "Tom", "age": 20}
print(user["name"])
print(user.get("email"))                 # 缺少时返回 None，不抛异常
print(user.get("city", "未知城市"))      # 可提供默认值

user["age"] = 21       # 已有键：修改
user["email"] = "tom@example.com"  # 新键：添加
user.update({"city": "上海", "vip": True})
user.setdefault("points", 0)  # 仅当键不存在时设置；适合初始化

print(list(user.keys()))
print(list(user.values()))
for key, value in user.items():
    # items() 每次给出 (key, value)，再由两个变量解包。
    print(f"{key} = {value}")

removed_email = user.pop("email", None)  # 默认值避免键不存在时 KeyError
del user["vip"]
print(removed_email, user)

stocks = {
    "600519": {"name": "贵州茅台", "price": 1688.0},
    "000001": {"name": "平安银行", "price": 10.5},
}
print(stocks["600519"]["price"])

# 字典推导式：键不能重复，后出现的值会覆盖先前值。
prices = {symbol: info["price"] for symbol, info in stocks.items()}
print(prices)

# ⚠️ user["missing"] 会 KeyError；不确定键是否存在时使用 get。
# ⚠️ dict 的键必须可哈希，list 不能作为键，str/number/tuple 通常可以。

"""
本节总结：[] 适合必须存在的键，get 适合可选键；items() 同时遍历键和值。
"""
