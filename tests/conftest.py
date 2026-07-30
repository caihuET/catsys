import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
logging.disable(logging.CRITICAL)

# 测试配置 - 使用 SQLite 避免依赖 MySQL
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PASSWORD"] = "test"
os.environ["MYSQL_DATABASE"] = "test_cat_sys"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ENV_MODE"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRY_MINUTES"] = "30"
os.environ["SMS_CODE_EXPIRE_SECONDS"] = "300"
os.environ["REG_LIMIT_COUNT"] = "3"
os.environ["REG_LIMIT_HOURS"] = "24"
os.environ["API_GATEWAY_PORT"] = "9002"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.shared.models import Base


@pytest.fixture(scope="session")
def test_engine():
    """创建内存 SQLite 引擎用于测试"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """创建独立的数据库会话，测试后回滚"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))
    yield session
    session.remove()
    transaction.rollback()
    connection.close()
