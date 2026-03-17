import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_transaction():
    return {
        "transaction_id": "txn_test_001",
        "user_id": "user_42",
        "amount": 150.00,
        "merchant_id": "merch_001",
        "merchant_category": "grocery",
        "location_lat": 40.7128,
        "location_lon": -74.0060,
        "timestamp": "2024-06-15T14:30:00",
    }


@pytest.fixture
def sample_user_history():
    base_time = datetime(2024, 6, 15, 9, 0, 0)
    return [
        {
            "amount": 50.0,
            "timestamp": (base_time + timedelta(hours=i)).isoformat(),
            "merchant_category": "grocery",
            "location_lat": 40.7128 + i * 0.001,
            "location_lon": -74.0060 + i * 0.001,
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_high_risk_transaction():
    return {
        "transaction_id": "txn_test_hr_001",
        "user_id": "user_99",
        "amount": 9500.00,
        "merchant_id": "merch_offshore",
        "merchant_category": "wire_transfer",
        "location_lat": 55.7558,
        "location_lon": 37.6173,
        "timestamp": "2024-06-15T03:15:00",
    }
