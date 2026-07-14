# -*- coding: utf-8 -*-
"""配置管理"""
import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Cat_Sys"))
    url_prefix: str = field(default_factory=lambda: os.getenv("URL_PREFIX", ""))
    env_mode: str = field(default_factory=lambda: os.getenv("ENV_MODE", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("LOG_LEVEL", "DEBUG") == "DEBUG")
    api_gateway_port: int = field(default_factory=lambda: int(os.getenv("API_GATEWAY_PORT", "9002")))
    domain: str = field(default_factory=lambda: os.getenv("DOMAIN", "localhost"))
    server_host: str = field(default_factory=lambda: os.getenv("SERVER_HOST", "0.0.0.0"))
    mysql_host: str = field(default_factory=lambda: os.getenv("MYSQL_HOST", "mysql"))
    mysql_port: int = field(default_factory=lambda: int(os.getenv("MYSQL_PORT", "3306")))
    mysql_user: str = field(default_factory=lambda: os.getenv("MYSQL_USER", "root"))
    mysql_password: str = field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    mysql_database: str = field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "cat_sys"))
    redis_host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "redis"))
    redis_port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    redis_password: str = field(default_factory=lambda: os.getenv("REDIS_PASSWORD", ""))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "dev-secret"))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiry_minutes: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRY_MINUTES", "30")))

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )


settings = AppConfig()
