import json
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.transaction import Transaction, FraudAlert


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, txn_data: dict) -> Transaction:
        txn = Transaction(
            transaction_id=txn_data["transaction_id"],
            user_id=txn_data["user_id"],
            amount=txn_data["amount"],
            merchant_id=txn_data["merchant_id"],
            merchant_category=txn_data["merchant_category"],
            location_lat=txn_data.get("location_lat"),
            location_lon=txn_data.get("location_lon"),
            timestamp=txn_data["timestamp"],
            fraud_probability=txn_data.get("fraud_probability"),
            risk_tier=txn_data.get("risk_tier"),
            shap_values=json.dumps(txn_data.get("shap_values", {})),
            status=txn_data.get("status", "pending"),
        )
        self.db.add(txn)
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def get_transaction(self, transaction_id: str) -> Transaction:
        return self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

    def list_transactions(self, page: int = 1, page_size: int = 50, user_id: str = None):
        query = self.db.query(Transaction)
        if user_id:
            query = query.filter(Transaction.user_id == user_id)

        total = query.count()
        transactions = (
            query.order_by(desc(Transaction.timestamp))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return transactions, total

    def get_user_history(self, user_id: str, limit: int = 100):
        txns = (
            self.db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.timestamp)
            .limit(limit)
            .all()
        )
        return [
            {
                "amount": t.amount,
                "timestamp": t.timestamp.isoformat(),
                "merchant_category": t.merchant_category,
                "location_lat": t.location_lat,
                "location_lon": t.location_lon,
            }
            for t in txns
        ]

    def get_flagged_transactions(self, page: int = 1, page_size: int = 50):
        query = self.db.query(Transaction).filter(
            Transaction.risk_tier.in_(["high", "critical"])
        )
        total = query.count()
        transactions = (
            query.order_by(desc(Transaction.timestamp))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return transactions, total

    def update_review(self, transaction_id: str, reviewer: str, action: str):
        txn = self.get_transaction(transaction_id)
        if not txn:
            return None
        txn.reviewed_by = reviewer
        txn.review_action = action
        txn.reviewed_at = datetime.utcnow()
        txn.status = "reviewed"
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def get_stats(self):
        total = self.db.query(func.count(Transaction.id)).scalar()
        flagged = self.db.query(func.count(Transaction.id)).filter(
            Transaction.risk_tier.in_(["high", "critical"])
        ).scalar()
        blocked = self.db.query(func.count(Transaction.id)).filter(
            Transaction.review_action == "block"
        ).scalar()
        avg_amount = self.db.query(func.avg(Transaction.amount)).scalar()

        return {
            "total_transactions": total or 0,
            "flagged_transactions": flagged or 0,
            "blocked_transactions": blocked or 0,
            "average_amount": round(float(avg_amount or 0), 2),
        }

    def create_alert(self, transaction_id: str, alert_type: str, severity: str, details: str):
        alert = FraudAlert(
            transaction_id=transaction_id,
            alert_type=alert_type,
            severity=severity,
            details=details,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
