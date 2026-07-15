from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from src.shared.database import get_db_sync
from src.shared.models import User, Employee, Merchant
import bcrypt, jwt, datetime

router = APIRouter()


class LoginRequest(BaseModel):
    phone: str
    password: str


class RegisterRequest(BaseModel):
    phone: str
    password: str
    business_name: str
    contact_person: str


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
def login(req: LoginRequest):
    db = get_db_sync()
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if user.status == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    emp = db.query(Employee).filter(Employee.user_id == user.id).first()
    if emp:
        merchant_id = emp.merchant_id
        role_code = emp.role_code
    else:
        m = db.query(Merchant).filter(Merchant.owner_user_id == user.id).first()
        merchant_id = m.id if m else 0
        role_code = user.user_type
    token = create_token(user.id, merchant_id, role_code)
    user.last_login = datetime.datetime.utcnow()
    db.commit()
    return {"code": 0, "data": {"token": token, "user_id": user.id, "merchant_id": merchant_id}}


@router.post("/auth/register")
def register(req: RegisterRequest):
    db = get_db_sync()
    if db.query(User).filter(User.phone == req.phone).first():
        raise HTTPException(status_code=409, detail="手机号已被注册")
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user = User(username=req.phone, phone=req.phone, password_hash=hashed,
                real_name=req.contact_person, user_type="merchant_owner")
    db.add(user)
    db.flush()
    merchant = Merchant(owner_user_id=user.id, business_name=req.business_name,
                        contact_person=req.contact_person, contact_phone=req.phone)
    db.add(merchant)
    db.commit()
    return {"code": 0, "data": {"user_id": user.id, "merchant_id": merchant.id}}
