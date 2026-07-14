# -*- coding: utf-8 -*-
"""????????"""
from src.shared.config import AppConfig

class TestAppConfig:
    def test_default_values(self):
        """???????"""
        config = AppConfig()
        assert config.app_name == "Cat_Sys"
        assert config.api_gateway_port == 9002
        assert config.jwt_expiry_minutes == 30

    def test_env_override(self):
        """????????"""
        import os
        os.environ["MYSQL_PASSWORD"] = "test123"
        config = AppConfig()
        assert config.mysql_password == "test123"

    def test_database_url(self):
        """????? URL ??"""
        config = AppConfig()
        url = config.database_url
        assert "mysql+pymysql" in url
        assert config.mysql_user in url
