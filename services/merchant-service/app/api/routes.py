from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.shared.database import get_db_sync
from src.shared.models import Merchant, Branch, Module, MerchantModule

router = APIRouter()

@router.get("/merchants")
def list_merchants():
    db = get_db_sync()
    merchants = db.query(Merchant).order_by(Merchant.id).all()
    return {"code": 0, "data": [{"id": m.id, "name": m.business_name, "status": m.status, "contact": m.contact_person, "phone": m.contact_phone, "expiry": str(m.expiry_date) if m.expiry_date else None, "registered": str(m.registered_at)} for m in merchants]}

@router.post("/merchants")
def create_merchant(name: str, contact: str, phone: str, owner_user_id: int):
    db = get_db_sync()
    merchant = Merchant(business_name=name, contact_person=contact, contact_phone=phone, owner_user_id=owner_user_id)
    db.add(merchant)
    db.commit()
    return {"code": 0, "data": {"id": merchant.id}}

@router.get("/branches")
def list_branches(merchant_id: int):
    db = get_db_sync()
    branches = db.query(Branch).filter(Branch.merchant_id == merchant_id).all()
    return {"code": 0, "data": [{"id": b.id, "name": b.name, "status": b.status} for b in branches]}

@router.post("/branches")
def create_branch(merchant_id: int, name: str):
    db = get_db_sync()
    branch = Branch(merchant_id=merchant_id, name=name)
    db.add(branch)
    db.commit()
    return {"code": 0, "data": {"id": branch.id}}

@router.get("/merchants/{mid}/modules")
def get_merchant_modules(mid: int):
    db = get_db_sync()
    enabled = {m.module_code for m in db.query(MerchantModule).filter(MerchantModule.merchant_id == mid, MerchantModule.is_enabled == True).all()}
    all_modules = db.query(Module).order_by(Module.sort_order).all()
    result = []
    for m in all_modules:
        en = m.module_type == "basic" or m.code in enabled
        result.append({"code": m.code, "name": m.name, "type": m.module_type, "enabled": en})
    return {"code": 0, "data": result}

@router.put("/merchants/{mid}/modules")
def update_merchant_modules(mid: int, modules: list):
    db = get_db_sync()
    db.query(MerchantModule).filter(MerchantModule.merchant_id == mid).delete()
    for code in modules:
        db.add(MerchantModule(merchant_id=mid, module_code=code, is_enabled=True))
    db.commit()
    return {"code": 0, "message": "模块配置已保存"}
