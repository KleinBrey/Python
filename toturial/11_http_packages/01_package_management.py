"""
==================================================
知识点：pip、venv、requirements.txt 与 pyproject.toml
==================================================

这是一份可运行的说明文件，不会真的安装或修改环境。
"""

commands = {
    "创建虚拟环境": "python -m venv .venv",
    "macOS/Linux 激活": "source .venv/bin/activate",
    "Windows 激活": r".venv\Scripts\activate",
    "安装包": "python -m pip install requests",
    "按依赖文件安装": "python -m pip install -r requirements.txt",
    "查看环境": "python -m pip list",
}
for purpose, command in commands.items():
    print(f"{purpose:14} {command}")

# 为什么推荐 python -m pip：明确使用“这个 python 解释器”对应的 pip，
# 避免电脑上多个 Python 时把包安装到错误环境。
# venv 为每个项目隔离依赖；不要把 .venv 提交到 Git。
# requirements.txt 常记录固定安装列表，例如 requests==2.32.4。
# pyproject.toml 是现代项目的统一配置入口，可描述包元数据、依赖、构建系统和工具配置。

"""
本节总结：每个项目使用独立 venv；用 python -m pip；应用依赖应记录并可复现。
"""
