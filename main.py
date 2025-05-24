import akshare as ak

from mongo import MongoDBHelper

db_helper = MongoDBHelper(db_name="python", collection_name="stock1")

db_helper2 = MongoDBHelper(db_name="python", collection_name="stock2")

stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()

# 打印数据类型
print(type(stock_sh_a_spot_em_df))

data_list = stock_sh_a_spot_em_df.to_dict(orient='records')

db_helper.insert_many(data_list)


print(stock_sh_a_spot_em_df)

stock_sse_summary_df = ak.stock_sse_summary()

stock_sse_summary_df_list = stock_sse_summary_df.to_dict(orient='records')

stock_szse_summary_df = ak.stock_szse_summary(date="20200619")

sstock_szse_summary_df_list = stock_szse_summary_df.to_dict(orient='records')


print(stock_szse_summary_df)


print(stock_sse_summary_df)

db_helper2.insert_many(sstock_szse_summary_df_list)


