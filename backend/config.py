"""应用配置管理 —— 所有配置集中在这里，从 .env 读取"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """公共配置（开发和生产环境共用的字段）"""

    model_config = SettingsConfigDict(
        env_file=".env",  # 读取哪个文件
        env_file_encoding="utf-8",
        extra="ignore",  # .env 里多余的变量忽略
    )

    # LLM 配置
    deepseek_api_key: str = ""  # 自动匹配 .env 里的 DEEPSEEK_API_KEY
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 数据库（Phase 1 用到，先留默认值）
    database_url: str = "sqlite+aiosqlite:///./codegenesis.db"
    redis_url: str = "redis://localhost:6379/0"

    # 应用配置
    app_env: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"


class DevSettings(Settings):
    """开发环境配置：打开调试、详细日志"""

    debug: bool = True
    log_level: str = "DEBUG"


class ProdSettings(Settings):
    """生产环境配置：关调试、警告级日志"""

    debug: bool = False
    log_level: str = "WARNING"


# 根据环境变量 APP_ENV 选择配置（默认开发环境）
settings: Settings
if os.getenv("APP_ENV") == "production":
    settings = ProdSettings()
else:
    settings = DevSettings()
