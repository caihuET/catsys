# -*- coding: utf-8 -*-
"""全局 SQLAlchemy 数据模型"""
import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Enum, Date, DateTime,
    Text, Boolean, ForeignKey, func, Numeric,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    """创建/更新时间戳混入"""
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class TenantMixin:
    """多租户混入"""
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)


# ===== user-service =====

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="登录名")
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, comment="手机号")
    email = Column(String(100))
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    user_type = Column(Enum("super_admin", "merchant_owner", "branch_employee"), nullable=False)
    status = Column(Enum("active", "disabled"), nullable=False, default="active")
    last_login = Column(DateTime)


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    current_branch_id = Column(Integer, ForeignKey("branches.id"), comment="当前工作分店")
    role_code = Column(Enum("manager", "sales", "care_staff"), nullable=False)
    job_title = Column(String(50))
    status = Column(Enum("active", "disabled"), nullable=False, default="active")
    hired_at = Column(DateTime, nullable=False, default=func.now())
    left_at = Column(DateTime)


# ===== merchant-service =====

class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String(100), nullable=False, comment="猫舍名称")
    business_license = Column(String(50))
    contact_person = Column(String(50), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    contact_email = Column(String(100))
    address = Column(String(255))
    logo_url = Column(String(255))
    status = Column(Enum("active", "suspended", "expired", "deleted"), nullable=False, default="active")
    expiry_date = Column(Date)
    registered_at = Column(DateTime, nullable=False, server_default=func.now())


class Branch(Base, TimestampMixin):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    contact_phone = Column(String(20))
    status = Column(Enum("active", "closed"), nullable=False, default="active")


class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    module_type = Column(Enum("basic", "advanced"), nullable=False)
    description = Column(String(255))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class MerchantModule(Base):
    __tablename__ = "merchant_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    module_code = Column(String(50), ForeignKey("modules.code"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    enabled_at = Column(DateTime, server_default=func.now())
    disabled_at = Column(DateTime)


# ===== cat-service =====

class Cat(Base, TenantMixin, TimestampMixin):
    __tablename__ = "cats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    breed = Column(String(50), comment="品种")
    color = Column(String(50), comment="毛色")
    gender = Column(Enum("male", "female"))
    birth_date = Column(Date)
    arrival_date = Column(Date, comment="到店日期")
    microchip_number = Column(String(50))
    pedigree_number = Column(String(50))
    status = Column(Enum("available", "reserved", "sold", "retired", "deceased", "fostering"),
                    nullable=False, default="available")
    live_status = Column(Enum("healthy", "weak", "needs_checkup", "needs_deworming"),
                         default="healthy", comment="活体状态")
    neutered_status = Column(Enum("pending", "neutered"), default="pending", comment="绝育情况")
    foster_end_date = Column(Date, comment="寄养结束日期")
    price = Column(Numeric(10, 2))
    photo_urls = Column(Text, comment="照片URL(JSON数组)")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))


class HealthRecord(Base, TenantMixin):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(Integer, ForeignKey("cats.id"), nullable=False, index=True)
    record_type = Column(Enum("vaccination", "deworming", "checkup", "illness", "surgery"), nullable=False)
    record_date = Column(Date, nullable=False)
    next_date = Column(Date, comment="下次日期")
    vaccine_type = Column(String(50))
    deworming_type = Column(String(50))
    vet_name = Column(String(50), comment="兽医")
    clinic = Column(String(100))
    result = Column(String(255))
    attachments = Column(Text, comment="附件(JSON)")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


# ===== crm-service =====

class Customer(Base, TenantMixin, TimestampMixin):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    wechat = Column(String(50))
    email = Column(String(100))
    address = Column(String(255))
    source = Column(String(50), comment="客户来源")
    status = Column(Enum("lead", "interested", "contracted", "owner", "lost"),
                    nullable=False, default="lead")
    preferred_breeds = Column(String(255))
    preferred_colors = Column(String(255))
    budget_min = Column(Numeric(10, 2))
    budget_max = Column(Numeric(10, 2))
    notes = Column(Text)


class Reservation(Base, TenantMixin, TimestampMixin):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cat_id = Column(Integer, ForeignKey("cats.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    reservation_date = Column(Date, nullable=False)
    deposit_amount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2))
    status = Column(Enum("active", "deposit_paid", "contracted", "completed", "cancelled"),
                    nullable=False, default="active")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))


class Contract(Base, TenantMixin, TimestampMixin):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    cat_id = Column(Integer, ForeignKey("cats.id"))
    contract_number = Column(String(50), unique=True, nullable=False)
    contract_type = Column(Enum("pet", "breeding"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2))
    remaining_amount = Column(Numeric(10, 2))
    sign_date = Column(Date, nullable=False)
    file_url = Column(String(255))
    status = Column(Enum("active", "fulfilled", "terminated"), nullable=False, default="active")
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))


class FollowupTask(Base, TenantMixin):
    __tablename__ = "followup_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    task_type = Column(Enum("followup", "birthday", "checkin", "custom"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    status = Column(Enum("pending", "completed", "cancelled"), nullable=False, default="pending")
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


# ===== finance-service =====

class Transaction(Base, TenantMixin):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("income", "expense"), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(String(255))
    related_type = Column(String(50))
    related_id = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


# ===== 审计日志 =====

class OperationLog(Base):
    __tablename__ = "operation_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service_name = Column(String(50), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"))
    merchant_id = Column(Integer)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(Integer)
    detail = Column(Text, comment="变更内容(JSON)")
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())
