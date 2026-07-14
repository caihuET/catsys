# -*- coding: utf-8 -*-
"""数据库连接与会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.shared.config import settings
from src.shared.models import Base

engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def init_db():
    """初始化数据库表结构"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话（含自动关闭）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync():
    """同步方式获取数据库会话"""
    db = SessionLocal()
    return db
