from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.shared.database import get_db_sync
from src.shared.models import User, Employee
import bcrypt, jwt, datetime

router = APIRouter()

def create_token(user_id: int, merchant_id: int = 0, role_code: str = "") -> str:
    from src.shared.config import settings
    payload = {
        "user_id": user_id,
        "merchant_id": merchant_id,
        "role_code": role_code,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

@router.post("/auth/login")
def login(phone: str, password: str):
    db = get_db_sync()
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        raise HTTPException(401, detail="账号或密码错误")
    if user.status == "disabled":
        raise HTTPException(403, detail="账号已被禁用")
    emp = db.query(Employee).filter(Employee.user_id == user.id).first()
    merchant_id = emp.merchant_id if emp else 0
    role_code = emp.role_code if emp else user.user_type
    token = create_token(user.id, merchant_id, role_code)
    user.last_login = datetime.datetime.utcnow()
    db.commit()
    return {"code": 0, "data": {"token": token, "user_id": user.id, "merchant_id": merchant_id, "role_code": role_code}}

@router.post("/auth/register")
def register(phone: str, password: str, business_name: str, contact_person: str):
    db = get_db_sync()
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(409, detail="手机号已被注册")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=phone, phone=phone, password_hash=hashed, real_name=contact_person, user_type="merchant_owner")
    db.add(user)
    db.flush()
    from src.shared.models import Merchant
    merchant = Merchant(owner_user_id=user.id, business_name=business_name, contact_person=contact_person, contact_phone=phone)
    db.add(merchant)
    db.commit()
    return {"code": 0, "data": {"user_id": user.id, "merchant_id": merchant.id}}

@router.post("/auth/switch-branch")
def switch_branch(user_id: int, branch_id: int):
    db = get_db_sync()
    emp = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not emp:
        raise HTTPException(404, detail="员工信息不存在")
    emp.current_branch_id = branch_id
    db.commit()
    token = create_token(user_id, emp.merchant_id, emp.role_code, branch_id)
    return {"code": 0, "data": {"token": token, "branch_id": branch_id}}
