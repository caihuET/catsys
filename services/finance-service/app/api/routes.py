from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.shared.database import get_db_sync
from src.shared.models import Transaction
import datetime

router = APIRouter()


class TransactionCreate(BaseModel):
    merchant_id: int
    branch_id: int
    type: str
    category: str
    amount: float
    transaction_date: str
    description: Optional[str] = None


@router.get("/transactions")
def list_transactions(branch_id: Optional[int] = None, merchant_id: Optional[int] = None,
                      type: Optional[str] = None, category: Optional[str] = None):
    db = get_db_sync()
    q = db.query(Transaction)
    if merchant_id: q = q.filter(Transaction.merchant_id == merchant_id)
    if branch_id: q = q.filter(Transaction.branch_id == branch_id)
    if type: q = q.filter(Transaction.type == type)
    if category: q = q.filter(Transaction.category == category)
    records = q.order_by(Transaction.transaction_date.desc()).all()
    return {"code": 0, "data": [{"id": t.id, "type": t.type, "category": t.category,
        "amount": float(t.amount), "transaction_date": str(t.transaction_date),
        "description": t.description} for t in records]}
