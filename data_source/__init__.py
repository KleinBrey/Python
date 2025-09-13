import tushare as ts

MY_TOKEN = 'b84edc56c8bee18697958fe5b8105df277a2179fee7966e026e57df6'

PRO_TOKEN = '94f520e0621fbeaef1471aa3e8c747e67d24898418d3412522f0fa60'

# 初始化 tushare
ts.set_token(MY_TOKEN)

tushare = ts.pro_api()