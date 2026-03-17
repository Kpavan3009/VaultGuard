from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    merchant_id = Column(String, nullable=False)
    merchant_category = Column(String, nullable=False)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    is_fraud = Column(Boolean, default=False)
    fraud_probability = Column(Float, nullable=True)
    risk_tier = Column(String, nullable=True)
    shap_values = Column(Text, nullable=True)
    status = Column(String, default="pending")
    reviewed_by = Column(String, nullable=True)
    review_action = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    alerts = relationship("FraudAlert", back_populates="transaction")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    avg_transaction_amount = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    last_transaction_at = Column(DateTime, nullable=True)
    common_merchant_categories = Column(Text, default="[]")
    common_locations = Column(Text, default="[]")


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="alerts")
