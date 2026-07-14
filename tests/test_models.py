# -*- coding: utf-8 -*-
"""????????"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.shared.models import Base, User, Merchant, Branch, Cat, Customer, Employee, Module, HealthRecord

class TestModels:
    @classmethod
    def setup_class(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def test_create_user(self):
        session = self.Session()
        user = User(username="test", password_hash="hash", real_name="??", user_type="merchant_owner")
        session.add(user)
        session.commit()
        assert user.id > 0
        assert user.username == "test"
        session.close()

    def test_all_tables_exist(self):
        """??????????"""
        tables = Base.metadata.tables
        required_tables = [
            "users", "employees", "merchants", "branches",
            "modules", "merchant_modules", "cats", "health_records",
            "customers", "reservations", "contracts",
            "followup_tasks", "transactions", "operation_logs",
        ]
        for table in required_tables:
            assert table in tables, f"? {table} ???"

    def test_cat_fields(self):
        """?????????"""
        columns = Base.metadata.tables["cats"].columns
        assert "arrival_date" in columns
        assert "live_status" in columns
        assert "neutered_status" in columns
        assert "foster_end_date" in columns
