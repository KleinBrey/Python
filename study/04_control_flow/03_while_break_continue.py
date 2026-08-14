"""
==================================================
知识点：while、break、continue 与 pass
==================================================
"""

attempt = 0
while attempt < 3:
    attempt += 1
    print(f"第 {attempt} 次尝试")

numbers = [1, -1, 2, 0, 3]
for number in numbers:
    if number < 0:
        continue  # 跳过本轮剩余代码，继续下一轮
    if number == 0:
        break     # 立即结束整个循环
    print("有效数字：", number)

# pass 什么也不做，只是语法占位。它不会“跳过一轮”，跳过应使用 continue。
def feature_to_build() -> None:
    pass

# 实际开发案例：有限次数重试。避免 while True 没有退出条件造成死循环。
max_retries = 3
for attempt in range(1, max_retries + 1):
    simulated_success = attempt == 2
    if simulated_success:
        print(f"第 {attempt} 次请求成功")
        break
    print(f"第 {attempt} 次请求失败")
else:
    print("所有重试均失败")

"""
练习：遍历 1~20，跳过 3 的倍数，遇到大于 15 时停止。

# ==========================
# 参考答案
# ==========================
for value in range(1, 21):
    if value > 15:
        break
    if value % 3 == 0:
        continue
    print(value)

本节总结：次数明确优先 for；条件驱动用 while；保证循环有退出路径。
"""
