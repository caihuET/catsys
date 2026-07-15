from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.shared.database import get_db_sync
from src.shared.models import Cat, HealthRecord
import datetime

router = APIRouter()


class CatCreate(BaseModel):
    merchant_id: int
    branch_id: int
    name: str
    breed: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    arrival_date: Optional[str] = None
    microchip_number: Optional[str] = None
    pedigree_number: Optional[str] = None
    status: str = "available"
    live_status: str = "healthy"
    neutered_status: str = "pending"
    foster_end_date: Optional[str] = None
    price: Optional[float] = None
    notes: Optional[str] = None


class HealthCreate(BaseModel):
    merchant_id: int
    branch_id: int
    cat_id: int
    record_type: str
    record_date: str
    next_date: Optional[str] = None
    vaccine_type: Optional[str] = None
    deworming_type: Optional[str] = None
    vet_name: Optional[str] = None
    clinic: Optional[str] = None
    result: Optional[str] = None
    notes: Optional[str] = None


def days_until(d):
    if not d:
        return None
    delta = d - datetime.date.today()
    return delta.days


@router.get("/cats")
def list_cats(branch_id: Optional[int] = None, merchant_id: Optional[int] = None,
              breed: Optional[str] = None, status: Optional[str] = None,
              live_status: Optional[str] = None, search: Optional[str] = None):
    db = get_db_sync()
    q = db.query(Cat)
    if merchant_id: q = q.filter(Cat.merchant_id == merchant_id)
    if branch_id: q = q.filter(Cat.branch_id == branch_id)
    if breed: q = q.filter(Cat.breed == breed)
    if status: q = q.filter(Cat.status == status)
    if live_status: q = q.filter(Cat.live_status == live_status)
    if search: q = q.filter(Cat.name.like(f"%{search}%"))
    cats = q.order_by(Cat.id).all()
    result = []
    for c in cats:
        age_days = (datetime.date.today() - c.birth_date).days if c.birth_date else None
        arrival_days = (datetime.date.today() - c.arrival_date).days if c.arrival_date else None
        result.append({
            "id": c.id, "name": c.name, "breed": c.breed, "color": c.color,
            "gender": c.gender, "age_days": age_days,
            "arrival_date": str(c.arrival_date) if c.arrival_date else None,
            "arrival_days": arrival_days,
            "live_status": c.live_status, "neutered_status": c.neutered_status,
            "foster_end_date": str(c.foster_end_date) if c.foster_end_date else None,
            "status": c.status, "price": float(c.price) if c.price else None,
        })
    return {"code": 0, "data": result}


@router.post("/cats")
def create_cat(req: CatCreate):
    db = get_db_sync()
    cat = Cat(**{k: v for k, v in req.dict().items() if v is not None})
    if req.birth_date:
        cat.birth_date = datetime.datetime.strptime(req.birth_date, "%Y-%m-%d").date()
    if req.arrival_date:
        cat.arrival_date = datetime.datetime.strptime(req.arrival_date, "%Y-%m-%d").date()
    if req.foster_end_date:
        cat.foster_end_date = datetime.datetime.strptime(req.foster_end_date, "%Y-%m-%d").date()
    db.add(cat)
    db.commit()
    return {"code": 0, "data": {"id": cat.id}}


@router.get("/cats/{cat_id}")
def get_cat(cat_id: int):
    db = get_db_sync()
    c = db.query(Cat).filter(Cat.id == cat_id).first()
    if not c:
        raise HTTPException(404, detail="cat not found")
    age_days = (datetime.date.today() - c.birth_date).days if c.birth_date else None
    arrival_days = (datetime.date.today() - c.arrival_date).days if c.arrival_date else None
    return {"code": 0, "data": {
        "id": c.id, "name": c.name, "breed": c.breed, "color": c.color,
        "gender": c.gender, "age_days": age_days,
        "arrival_date": str(c.arrival_date) if c.arrival_date else None,
        "arrival_days": arrival_days,
        "live_status": c.live_status, "neutered_status": c.neutered_status,
        "foster_end_date": str(c.foster_end_date) if c.foster_end_date else None,
        "status": c.status, "price": float(c.price) if c.price else None,
        "notes": c.notes,
    }}


@router.put("/cats/{cat_id}")
def update_cat(cat_id: int, req: CatCreate):
    db = get_db_sync()
    c = db.query(Cat).filter(Cat.id == cat_id).first()
    if not c:
        raise HTTPException(404, detail="cat not found")
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            setattr(c, k, v)
    if req.birth_date:
        c.birth_date = datetime.datetime.strptime(req.birth_date, "%Y-%m-%d").date()
    if req.arrival_date:
        c.arrival_date = datetime.datetime.strptime(req.arrival_date, "%Y-%m-%d").date()
    if req.foster_end_date:
        c.foster_end_date = datetime.datetime.strptime(req.foster_end_date, "%Y-%m-%d").date()
    db.commit()
    return {"code": 0, "message": "updated"}


@router.get("/health", tags=["Health"])
def list_health(cat_id: Optional[int] = None, merchant_id: Optional[int] = None,
                record_type: Optional[str] = None, vet_name: Optional[str] = None):
    db = get_db_sync()
    q = db.query(HealthRecord)
    if cat_id: q = q.filter(HealthRecord.cat_id == cat_id)
    if merchant_id: q = q.filter(HealthRecord.merchant_id == merchant_id)
    if record_type: q = q.filter(HealthRecord.record_type == record_type)
    if vet_name: q = q.filter(HealthRecord.vet_name.like(f"%{vet_name}%"))
    records = q.order_by(HealthRecord.record_date.desc()).all()
    return {"code": 0, "data": [{
        "id": r.id, "cat_id": r.cat_id, "record_type": r.record_type,
        "record_date": str(r.record_date), "next_date": str(r.next_date) if r.next_date else None,
        "days_until": days_until(r.next_date),
        "vaccine_type": r.vaccine_type, "deworming_type": r.deworming_type,
        "vet_name": r.vet_name, "clinic": r.clinic, "result": r.result, "notes": r.notes,
    } for r in records]}


@router.post("/health", tags=["Health"])
def create_health(req: HealthCreate):
    db = get_db_sync()
    h = HealthRecord(**{k: v for k, v in req.dict().items() if v is not None})
    h.record_date = datetime.datetime.strptime(req.record_date, "%Y-%m-%d").date()
    if req.next_date:
        h.next_date = datetime.datetime.strptime(req.next_date, "%Y-%m-%d").date()
    db.add(h)
    db.commit()
    return {"code": 0, "data": {"id": h.id}}
