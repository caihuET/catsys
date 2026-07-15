from fastapi import APIRouter
from sqlalchemy import func
from src.shared.database import get_db_sync
from src.shared.models import Cat, Customer, Reservation, FollowupTask, HealthRecord

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(merchant_id: int, branch_id: int = None):
    db = get_db_sync()
    def bf(q): return q.filter(Cat.branch_id == branch_id) if branch_id else q
    cats = bf(db.query(func.count(Cat.id)).filter(Cat.merchant_id == merchant_id)).scalar() or 0
    customers = bf(db.query(func.count(Customer.id)).filter(Customer.merchant_id == merchant_id)).scalar() or 0
    active_res = bf(db.query(func.count(Reservation.id)).filter(
        Reservation.merchant_id == merchant_id, Reservation.status.in_(["active", "deposit_paid"]))).scalar() or 0
    pending_tasks = bf(db.query(func.count(FollowupTask.id)).filter(
        FollowupTask.merchant_id == merchant_id, FollowupTask.status == "pending")).scalar() or 0
    return {"code": 0, "data": {
        "total_cats": cats, "total_customers": customers,
        "active_reservations": active_res, "pending_tasks": pending_tasks,
    }}
