import os

import tushare as ts

DEFAULT_TUSHARE_TOKEN = "b84edc56c8bee18697958fe5b8105df277a2179fee7966e026e57df6"
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", DEFAULT_TUSHARE_TOKEN)

# 直接在内存中传入 token，避免运行时写入 ~/tk.csv
tushare = ts.pro_api(TUSHARE_TOKEN)
