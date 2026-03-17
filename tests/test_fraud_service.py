import pytest

from app.services.fraud_service import FraudDetectionService


@pytest.fixture(scope="module")
def fraud_service():
    return FraudDetectionService(model_path="models/")


def test_predict_returns_valid_structure(fraud_service, sample_user_history):
    txn = {
        "transaction_id": "t_pred_001",
        "user_id": "u1",
        "amount": 250.0,
        "merchant_category": "grocery",
        "location_lat": 40.7128,
        "location_lon": -74.0060,
        "timestamp": "2024-06-15T14:30:00",
    }
    result = fraud_service.predict(txn, sample_user_history)
    assert "fraud_probability" in result
    assert "risk_tier" in result
    assert "top_features" in result
    assert "recommended_action" in result
    assert isinstance(result["fraud_probability"], float)
    assert 0.0 <= result["fraud_probability"] <= 1.0


def test_predict_returns_shap_values(fraud_service):
    txn = {
        "transaction_id": "t_pred_002",
        "user_id": "u2",
        "amount": 100.0,
        "merchant_category": "dining",
        "location_lat": 40.0,
        "location_lon": -74.0,
        "timestamp": "2024-06-15T12:00:00",
    }
    result = fraud_service.predict(txn)
    assert "all_shap_values" in result
    assert isinstance(result["all_shap_values"], dict)
    assert len(result["all_shap_values"]) == 17


def test_risk_tier_critical():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._get_risk_tier(0.85) == "critical"


def test_risk_tier_high():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._get_risk_tier(0.55) == "high"


def test_risk_tier_medium():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._get_risk_tier(0.35) == "medium"


def test_risk_tier_low():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._get_risk_tier(0.1) == "low"


def test_risk_tier_boundary_values():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._get_risk_tier(0.8) == "critical"
    assert svc._get_risk_tier(0.5) == "high"
    assert svc._get_risk_tier(0.2) == "medium"
    assert svc._get_risk_tier(0.0) == "low"


def test_recommend_action_maps_correctly():
    svc = FraudDetectionService.__new__(FraudDetectionService)
    assert svc._recommend_action("critical") == "block_transaction"
    assert svc._recommend_action("high") == "require_verification"
    assert svc._recommend_action("medium") == "flag_for_review"
    assert svc._recommend_action("low") == "approve"
