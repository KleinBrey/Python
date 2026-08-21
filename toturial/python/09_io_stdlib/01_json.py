"""
==================================================
知识点：JSON 与 Python 对象转换
==================================================
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

json_text = '{"symbol": "600519", "price": 1688.0, "active": true, "note": null}'
data = json.loads(json_text)  # loads：从 str 加载（s 可记作 string）
print(data, type(data), data["note"])

# dumps：转为 JSON 字符串。ensure_ascii=False 保留中文；indent 便于人读。
output = json.dumps(
    {"name": "贵州茅台", "prices": [1680.0, 1688.0]},
    ensure_ascii=False,
    indent=2,
)
print(output)

with TemporaryDirectory() as directory:
    path = Path(directory) / "stock.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)  # dump 写文件对象
    with path.open("r", encoding="utf-8") as file:
        loaded = json.load(file)  # load 读文件对象
    print(loaded)

# JSON object ↔ dict；array ↔ list；true/false ↔ True/False；null ↔ None。
# JSON 不支持 datetime、set、自定义类；需要先转换为字符串/列表/字典。

"""
本节总结：loads/dumps 处理字符串，load/dump 处理文件；JSON object 对应 dict。
"""
