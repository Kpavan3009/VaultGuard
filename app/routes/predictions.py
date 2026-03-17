from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import TransactionCreate, FraudPredictionResponse
from app.services.fraud_service import FraudDetectionService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/predictions", tags=["predictions"])

fraud_service = FraudDetectionService()


@router.post("/analyze", response_model=FraudPredictionResponse)
def analyze_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    txn_svc = TransactionService(db)
    user_history = txn_svc.get_user_history(txn.user_id)

    txn_dict = txn.model_dump()
    txn_dict["timestamp"] = txn.timestamp.isoformat()

    result = fraud_service.predict(txn_dict, user_history)

    txn_dict["fraud_probability"] = result["fraud_probability"]
    txn_dict["risk_tier"] = result["risk_tier"]
    txn_dict["shap_values"] = result["all_shap_values"]
    txn_dict["timestamp"] = txn.timestamp
    txn_dict["status"] = result["recommended_action"]

    db_txn = txn_svc.get_transaction(txn.transaction_id)
    if not db_txn:
        txn_svc.create_transaction(txn_dict)

    if result["risk_tier"] in ("high", "critical"):
        txn_svc.create_alert(
            transaction_id=txn.transaction_id,
            alert_type="fraud_detection",
            severity=result["risk_tier"],
            details=f"fraud probability: {result['fraud_probability']}",
        )

    return FraudPredictionResponse(
        transaction_id=txn.transaction_id,
        fraud_probability=result["fraud_probability"],
        risk_tier=result["risk_tier"],
        top_features=result["top_features"],
        recommended_action=result["recommended_action"],
    )


@router.post("/batch")
def batch_analyze(transactions: list[TransactionCreate], db: Session = Depends(get_db)):
    results = []
    txn_svc = TransactionService(db)

    for txn in transactions:
        user_history = txn_svc.get_user_history(txn.user_id)
        txn_dict = txn.model_dump()
        txn_dict["timestamp"] = txn.timestamp.isoformat()
        result = fraud_service.predict(txn_dict, user_history)
        results.append({
            "transaction_id": txn.transaction_id,
            "fraud_probability": result["fraud_probability"],
            "risk_tier": result["risk_tier"],
            "recommended_action": result["recommended_action"],
        })

    return {"results": results, "total": len(results)}
