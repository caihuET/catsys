from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.shared.database import get_db_sync
from src.shared.models import Merchant, Branch, Module, MerchantModule, User
import datetime

router = APIRouter()


class MerchantCreate(BaseModel):
    business_name: str
    contact_person: str
    contact_phone: str
    owner_user_id: int
    business_license: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    expiry_date: Optional[str] = None


class BranchCreate(BaseModel):
    merchant_id: int
    name: str
    address: Optional[str] = None
    contact_phone: Optional[str] = None


class ModuleConfigUpdate(BaseModel):
    modules: List[str]


@router.get("/merchants")
def list_merchants(status: Optional[str] = None, search: Optional[str] = None):
    db = get_db_sync()
    q = db.query(Merchant)
    if status:
        q = q.filter(Merchant.status == status)
    if search:
        q = q.filter(Merchant.business_name.like(f"%{search}%") | Merchant.contact_person.like(f"%{search}%"))
    result = []
    for m in q.order_by(Merchant.id).all():
        remaining = (m.expiry_date - datetime.date.today()).days if m.expiry_date else None
        result.append({"id": m.id, "business_name": m.business_name, "contact_person": m.contact_person,
            "contact_phone": m.contact_phone, "status": m.status,
            "expiry_date": str(m.expiry_date) if m.expiry_date else None,
            "remaining_days": remaining, "registered_at": str(m.registered_at)})
    return {"code": 0, "data": result}


@router.post("/merchants")
def create_merchant(req: MerchantCreate):
    db = get_db_sync()
    m = Merchant(owner_user_id=req.owner_user_id, business_name=req.business_name,
                 contact_person=req.contact_person, contact_phone=req.contact_phone)
    if req.expiry_date:
        m.expiry_date = datetime.datetime.strptime(req.expiry_date, "%Y-%m-%d").date()
    db.add(m)
    db.commit()
    return {"code": 0, "data": {"id": m.id}}


@router.get("/merchants/{merchant_id}")
def get_merchant(merchant_id: int):
    db = get_db_sync()
    m = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not m:
        raise HTTPException(404, detail="merchant not found")
    remaining = (m.expiry_date - datetime.date.today()).days if m.expiry_date else None
    return {"code": 0, "data": {"id": m.id, "business_name": m.business_name,
        "status": m.status, "expiry_date": str(m.expiry_date) if m.expiry_date else None,
        "remaining_days": remaining}}


@router.get("/branches")
def list_branches(merchant_id: int):
    db = get_db_sync()
    branches = db.query(Branch).filter(Branch.merchant_id == merchant_id).all()
    return {"code": 0, "data": [{"id": b.id, "name": b.name, "address": b.address,
        "contact_phone": b.contact_phone, "status": b.status} for b in branches]}


@router.post("/branches")
def create_branch(req: BranchCreate):
    db = get_db_sync()
    b = Branch(merchant_id=req.merchant_id, name=req.name)
    db.add(b)
    db.commit()
    return {"code": 0, "data": {"id": b.id}}


@router.delete("/branches/{branch_id}")
def delete_branch(branch_id: int):
    db = get_db_sync()
    b = db.query(Branch).filter(Branch.id == branch_id).first()
    if not b:
        raise HTTPException(404, detail="branch not found")
    b.status = "closed"
    db.commit()
    return {"code": 0, "message": "branch closed"}


@router.get("/modules")
def list_modules():
    db = get_db_sync()
    modules = db.query(Module).order_by(Module.sort_order).all()
    return {"code": 0, "data": [{"code": m.code, "name": m.name,
        "module_type": m.module_type} for m in modules]}


@router.get("/merchants/{merchant_id}/modules")
def get_merchant_modules(merchant_id: int):
    db = get_db_sync()
    enabled = {mm.module_code for mm in db.query(MerchantModule).filter(
        MerchantModule.merchant_id == merchant_id, MerchantModule.is_enabled == True).all()}
    all_mods = db.query(Module).order_by(Module.sort_order).all()
    return {"code": 0, "data": [{"code": m.code, "name": m.name,
        "type": m.module_type, "enabled": m.module_type == "basic" or m.code in enabled} for m in all_mods]}


@router.put("/merchants/{merchant_id}/modules")
def update_merchant_modules(merchant_id: int, req: ModuleConfigUpdate):
    db = get_db_sync()
    db.query(MerchantModule).filter(MerchantModule.merchant_id == merchant_id).delete()
    for code in req.modules:
        db.add(MerchantModule(merchant_id=merchant_id, module_code=code, is_enabled=True))
    db.commit()
    return {"code": 0, "message": "modules saved"}
