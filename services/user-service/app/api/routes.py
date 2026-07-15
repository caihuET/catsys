import logging
from fastapi import APIRouter, HTTPException, Request
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
    code: str  # 短信验证码
    client_id: str = ""  # 设备标识


class SendCodeRequest(BaseModel):
    phone: str
    type: str = "register"  # register | reset


class ResetPasswordRequest(BaseModel):
    phone: str
    password: str
    code: str


def create_token(user_id: int, merchant_id: int = 0, role_code: str = "") -> str:
    from src.shared.config import settings
    payload = {
        "user_id": user_id,
        "merchant_id": merchant_id,
        "role_code": role_code,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_client_ip() -> str:
    """辅助函数: 获取请求 IP（待 FastAPI 注入）"""
    pass


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


@router.post("/auth/send-code")
def send_code(req: SendCodeRequest, request: Request = None):
    """发送短信验证码"""
    from src.shared.config import settings
    from service.sms import send_sms
    # 校验手机号格式
    if not req.phone or len(req.phone) < 11:
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    result = send_sms(req.phone)
    if result["success"]:
        return {"code": 0, "message": "验证码已发送"}
    else:
        logger.warning("短信发送失败: %s", result.get("message"))
        return {"code": 0, "message": "验证码已发送（mock模式）"}


@router.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest):
    """重置密码"""
    from ..service.sms import verify_code
    if not verify_code(req.phone, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    import bcrypt
    db = get_db_sync()
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="该手机号未注册")
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user.password_hash = hashed
    db.commit()
    return {"code": 0, "message": "密码重置成功"}


@router.post("/auth/register")
def register(req: RegisterRequest, request: Request = None):
    from service.sms import verify_code, check_reg_rate_limit, increment_reg_count
    # 1. 校验短信验证码
    if not verify_code(req.phone, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    # 2. 检查注册频率限制（IP + 设备标识）
    # 从请求头获取真实 IP
    ip = "unknown"
    client_id = req.client_id or ""
    if request:
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
    allowed, current_count = check_reg_rate_limit(ip, client_id)
    if not allowed:
        from src.shared.config import settings
        raise HTTPException(
            status_code=429,
            detail=f"同一IP同一设备24小时内最多注册{settings.reg_limit_count}个账号，已达上限",
        )
    # 3. 原有注册逻辑
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
    # 4. 注册成功后增加频率计数
    increment_reg_count(ip, client_id)
    return {"code": 0, "data": {"user_id": user.id, "merchant_id": merchant.id}}
