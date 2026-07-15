from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.shared.database import get_db_sync
from src.shared.models import Customer, Reservation, Contract, FollowupTask
import datetime

router = APIRouter()


class CustomerCreate(BaseModel):
    merchant_id: int
    branch_id: int
    name: str
    phone: Optional[str] = None
    wechat: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    source: Optional[str] = None
    status: str = "lead"
    preferred_breeds: Optional[str] = None
    preferred_colors: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    notes: Optional[str] = None


class ReservationCreate(BaseModel):
    merchant_id: int
    branch_id: int
    cat_id: Optional[int] = None
    customer_id: int
    reservation_date: str
    deposit_amount: float = 0
    total_price: Optional[float] = None
    notes: Optional[str] = None


@router.get("/customers")
def list_customers(branch_id: Optional[int] = None, merchant_id: Optional[int] = None,
                   status: Optional[str] = None, search: Optional[str] = None):
    db = get_db_sync()
    q = db.query(Customer)
    if merchant_id: q = q.filter(Customer.merchant_id == merchant_id)
    if branch_id: q = q.filter(Customer.branch_id == branch_id)
    if status: q = q.filter(Customer.status == status)
    if search: q = q.filter(Customer.name.like(f"%{search}%") | Customer.phone.like(f"%{search}%"))
    customers = q.order_by(Customer.id).all()
    return {"code": 0, "data": [{"id": c.id, "name": c.name, "phone": c.phone,
        "wechat": c.wechat, "source": c.source, "status": c.status,
        "preferred_breeds": c.preferred_breeds} for c in customers]}


@router.post("/customers")
def create_customer(req: CustomerCreate):
    db = get_db_sync()
    c = Customer(**{k: v for k, v in req.dict().items() if v is not None})
    db.add(c); db.commit()
    return {"code": 0, "data": {"id": c.id}}


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    db = get_db_sync()
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c: raise HTTPException(404, detail="not found")
    return {"code": 0, "data": {"id": c.id, "name": c.name, "phone": c.phone,
        "wechat": c.wechat, "email": c.email, "address": c.address,
        "source": c.source, "status": c.status, "preferred_breeds": c.preferred_breeds,
        "preferred_colors": c.preferred_colors, "budget_min": float(c.budget_min) if c.budget_min else None,
        "budget_max": float(c.budget_max) if c.budget_max else None, "notes": c.notes}}


@router.put("/customers/{customer_id}")
def update_customer(customer_id: int, req: CustomerCreate):
    db = get_db_sync()
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c: raise HTTPException(404, detail="not found")
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None: setattr(c, k, v)
    db.commit()
    return {"code": 0, "message": "updated"}


@router.get("/reservations")
def list_reservations(branch_id: Optional[int] = None, merchant_id: Optional[int] = None,
                      status: Optional[str] = None):
    db = get_db_sync()
    q = db.query(Reservation)
    if merchant_id: q = q.filter(Reservation.merchant_id == merchant_id)
    if branch_id: q = q.filter(Reservation.branch_id == branch_id)
    if status: q = q.filter(Reservation.status == status)
    reservations = q.order_by(Reservation.id).all()
    return {"code": 0, "data": [{"id": r.id, "customer_id": r.customer_id, "cat_id": r.cat_id,
        "deposit_amount": float(r.deposit_amount) if r.deposit_amount else 0,
        "total_price": float(r.total_price) if r.total_price else None,
        "status": r.status, "reservation_date": str(r.reservation_date)} for r in reservations]}


@router.post("/reservations")
def create_reservation(req: ReservationCreate):
    db = get_db_sync()
    r = Reservation(**{k: v for k, v in req.dict().items() if v is not None})
    r.reservation_date = datetime.datetime.strptime(req.reservation_date, "%Y-%m-%d").date()
    db.add(r); db.commit()
    return {"code": 0, "data": {"id": r.id}}


@router.get("/tasks")
def list_tasks(branch_id: Optional[int] = None, merchant_id: Optional[int] = None,
               status: Optional[str] = None, task_type: Optional[str] = None):
    db = get_db_sync()
    q = db.query(FollowupTask)
    if merchant_id: q = q.filter(FollowupTask.merchant_id == merchant_id)
    if branch_id: q = q.filter(FollowupTask.branch_id == branch_id)
    if status: q = q.filter(FollowupTask.status == status)
    if task_type: q = q.filter(FollowupTask.task_type == task_type)
    tasks = q.order_by(FollowupTask.due_date).all()
    return {"code": 0, "data": [{"id": t.id, "customer_id": t.customer_id,
        "task_type": t.task_type, "title": t.title, "description": t.description,
        "due_date": str(t.due_date) if t.due_date else None,
        "days_until": (t.due_date - datetime.date.today()).days if t.due_date else None,
        "status": t.status} for t in tasks]}


@router.put("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    db = get_db_sync()
    t = db.query(FollowupTask).filter(FollowupTask.id == task_id).first()
    if not t: raise HTTPException(404, detail="task not found")
    if t.status == "cancelled" or (t.due_date and t.due_date < datetime.date.today() and t.status != "completed"):
        raise HTTPException(400, detail="expired task cannot be completed")
    t.status = "completed"
    t.completed_at = datetime.datetime.utcnow()
    db.commit()
    return {"code": 0, "message": "completed"}
