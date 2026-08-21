"""
==================================================
知识点：BaseSettings 与 SettingsConfigDict
==================================================

先安装：python -m pip install pydantic-settings
"""

import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    print("缺少 pydantic-settings，请运行：python -m pip install pydantic-settings")
else:
    class Settings(BaseSettings):
        """环境变量前缀为 APP_，例如 APP_DEBUG=true。"""
        model_config = SettingsConfigDict(
            env_prefix="APP_",
            env_file=".env",
            extra="ignore",
        )

        api_url: str = "https://example.invalid"
        timeout: float = 10.0
        debug: bool = False

    # 为了案例可重复且不依赖真实 .env，临时设置一个非敏感环境变量。
    os.environ.setdefault("APP_TIMEOUT", "5.5")
    settings = Settings()
    print(settings.model_dump())

# BaseSettings 按字段类型解析环境变量；真实密码不要写进代码或提交到 Git。
# 优先级与 .env 行为可配置，团队应在 README 中记录所需变量。

"""
本节总结：BaseSettings 将环境配置解析成带类型对象；SettingsConfigDict 定义读取规则。
"""
