"""
==================================================
知识点：pathlib 与文本文件
==================================================
"""

from pathlib import Path
from tempfile import TemporaryDirectory

current_file = Path(__file__)
print("当前文件：", current_file)
print("父目录：", current_file.parent)
print("文件名：", current_file.name)
print("后缀：", current_file.suffix)
print("是否存在：", current_file.exists())

with TemporaryDirectory() as directory:
    data_dir = Path(directory) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    text_path = data_dir / "prices.txt"  # / 运算符安全拼接路径

    # encoding="utf-8" 避免不同操作系统默认编码不同导致乱码。
    text_path.write_text("600519,1688.0\n000001,10.5\n", encoding="utf-8")
    content = text_path.read_text(encoding="utf-8")
    print(content)

    # 经典 open API。with 退出时自动关闭文件，即使读取过程出现异常。
    with text_path.open("r", encoding="utf-8") as file:
        print("readline：", file.readline().strip())
        print("readlines：", file.readlines())

    with text_path.open("a", encoding="utf-8") as file:
        file.write("300750,220.0\n")  # a 追加；w 会清空旧内容再写

    with text_path.open("r", encoding="utf-8") as file:
        for line in file:  # 大文件逐行遍历，不必一次性读入内存
            print("逐行：", line.strip())

"""
本节总结：现代路径操作首选 Path；文本明确 UTF-8；文件用 with 自动关闭。
"""
