"""
==================================================
知识点：loc、iloc、条件筛选与排序
==================================================
"""

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请运行：python -m pip install pandas")
else:
    frame = pd.DataFrame(
        {
            "symbol": ["600519", "000001", "300750"],
            "close": [1688.0, 10.5, 220.0],
            "volume": [1200, 5000, 3200],
        }
    )
    print(frame["close"])                  # 单列 -> Series
    print(frame[["symbol", "close"]])     # 多列 -> DataFrame
    print(frame.loc[0:1, ["symbol", "close"]])  # loc 按标签，结束标签包含
    print(frame.iloc[0:2, 0:2])            # iloc 按整数位置，结束位置不包含

    expensive = frame.loc[frame["close"] > 100, ["symbol", "close"]]
    print(expensive)

    # 多条件必须分别加括号，并用 & / |，不能直接用 and/or。
    active = frame[(frame["close"] > 100) & (frame["volume"] >= 2000)]
    print(active)
    print(frame.sort_values(["volume", "close"], ascending=[False, True]))

    # 推荐用 loc 明确赋值，避免链式赋值是否生效的不确定性。
    frame.loc[frame["symbol"] == "000001", "close"] = 10.6
    print(frame)

"""
本节总结：loc 按标签，iloc 按位置；条件用括号和 &/|；赋值优先 loc。
"""
