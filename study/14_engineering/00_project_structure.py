"""
==================================================
知识点：真实 Python 项目结构
==================================================
"""

responsibilities = {
    "app/api": "HTTP/命令行入口：接收输入、调用服务、返回输出",
    "app/core": "配置、日志、通用基础设施，不放具体业务流程",
    "app/database": "数据库连接、建表、事务等底层设施",
    "app/models": "领域对象、请求响应模型、数据结构",
    "app/providers": "对接外部 API、文件、行情数据源",
    "app/repositories": "封装数据持久化与查询，不承载业务决策",
    "app/services": "组织用例和业务规则，协调 provider/repository",
    "scripts": "一次性运维、数据迁移、导入导出脚本",
    "tests": "自动化测试，与生产代码结构大致对应",
}
for directory, purpose in responsibilities.items():
    print(f"{directory:18} {purpose}")

print(
    """
project/
├── app/
│   ├── api/          ├── core/       ├── database/
│   ├── models/       ├── providers/  ├── repositories/
│   └── services/
├── scripts/
├── tests/
├── pyproject.toml
└── README.md
"""
)

# 小项目不要为了“标准”创建大量空目录；当职责真的出现时再拆分。
# README 说明如何安装/运行/测试；pyproject.toml 记录依赖和工具配置。

"""
本节总结：按职责分层是为了降低耦合；Service 编排业务，Repository 管持久化。
"""
