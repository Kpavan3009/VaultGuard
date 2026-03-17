from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionBase(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant_id: str
    merchant_category: str
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    timestamp: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    is_fraud: bool
    fraud_probability: Optional[float] = None
    risk_tier: Optional[str] = None
    status: str

    model_config = {"from_attributes": True}


class FraudPredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    risk_tier: str
    top_features: list[dict]
    recommended_action: str


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int


class AlertResponse(BaseModel):
    id: int
    transaction_id: str
    alert_type: str
    severity: str
    details: str
    acknowledged: bool
    created_at: datetime

    model_config = {"from_attributes": True}
