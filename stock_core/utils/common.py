import pandas as pd

def show_all_pandas():
    """设置 pandas 的显示选项，方便调试和查看数据"""
    pd.set_option("display.max_columns", None)      # 显示所有列
    pd.set_option("display.max_rows", None)         # 显示所有行
    pd.set_option("display.width", None)            # 不自动换行
    pd.set_option("display.max_colwidth", None)     # 不截断列内容
    pd.set_option("display.unicode.east_asian_width", True)  # 中英文对齐



def rename_columns(df,column_map) :
    """将列名替换"""
    return df.rename(columns=column_map)


def load_from_mongodb(collection) -> pd.DataFrame:
    """从 MongoDB 加载数据到 Pandas DataFrame"""
    try:
        data = collection.find_many({})
        df = pd.DataFrame(list(data))
        if "_id" in df.columns:
            df = df.drop(columns=["_id"])
        print("✅ 数据已从 MongoDB 加载!")
        return df
    except Exception as e:
        print(f"❌ 从 MongoDB 加载数据失败: {e}")
        return pd.DataFrame()


def save_to_mongo(df: pd.DataFrame,collection) -> None:
    """保存结果到 MongoDB"""
    try:
        collection.delete_many({})
        collection.insert_many(df.to_dict(orient="records"))
        print("✅ 数据已保存到 MongoDB!")
    except Exception as e:
        print(f"❌ 保存到 MongoDB 失败: {e}")