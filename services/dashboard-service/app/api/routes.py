from fastapi import APIRouter
from sqlalchemy import func
from src.shared.database import get_db_sync
from src.shared.models import Cat, Customer, Reservation, FollowupTask, HealthRecord

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(merchant_id: int, branch_id: int = None):
    db = get_db_sync()
    
    q_cat = db.query(func.count(Cat.id))
    if merchant_id: q_cat = q_cat.filter(Cat.merchant_id == merchant_id)
    cats = q_cat.scalar() or 0
    
    q_cust = db.query(func.count(Customer.id))
    if merchant_id: q_cust = q_cust.filter(Customer.merchant_id == merchant_id)
    customers = q_cust.scalar() or 0
    
    q_res = db.query(func.count(Reservation.id)).filter(Reservation.status.in_(["active", "deposit_paid"]))
    if merchant_id: q_res = q_res.filter(Reservation.merchant_id == merchant_id)
    active_res = q_res.scalar() or 0
    
    q_task = db.query(func.count(FollowupTask.id)).filter(FollowupTask.status == "pending")
    if merchant_id: q_task = q_task.filter(FollowupTask.merchant_id == merchant_id)
    pending_tasks = q_task.scalar() or 0
    
    return {"code": 0, "data": {
        "total_cats": cats, "total_customers": customers,
        "active_reservations": active_res, "pending_tasks": pending_tasks,
    }}
