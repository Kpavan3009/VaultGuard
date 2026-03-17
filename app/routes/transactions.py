from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    svc = TransactionService(db)
    existing = svc.get_transaction(txn.transaction_id)
    if existing:
        raise HTTPException(status_code=409, detail="transaction already exists")
    result = svc.create_transaction(txn.model_dump())
    return result


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    svc = TransactionService(db)
    txn = svc.get_transaction(transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="transaction not found")
    return txn


@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: str = None,
    db: Session = Depends(get_db),
):
    svc = TransactionService(db)
    transactions, total = svc.list_transactions(page, page_size, user_id)
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/flagged/list", response_model=TransactionListResponse)
def list_flagged(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    svc = TransactionService(db)
    transactions, total = svc.get_flagged_transactions(page, page_size)
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{transaction_id}/review")
def review_transaction(
    transaction_id: str,
    reviewer: str = Query(...),
    action: str = Query(...),
    db: Session = Depends(get_db),
):
    svc = TransactionService(db)
    txn = svc.update_review(transaction_id, reviewer, action)
    if not txn:
        raise HTTPException(status_code=404, detail="transaction not found")
    return {"status": "reviewed", "transaction_id": transaction_id}


@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    svc = TransactionService(db)
    return svc.get_stats()
