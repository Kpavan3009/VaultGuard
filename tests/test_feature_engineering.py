import numpy as np
import pandas as pd
import pytest
from datetime import datetime, timedelta

from app.ml.feature_engineering import (
    haversine,
    compute_features,
    compute_single_transaction_features,
    CATEGORY_MAP,
)


def test_haversine_same_point():
    result = haversine(40.7128, -74.0060, 40.7128, -74.0060)
    assert result == pytest.approx(0.0, abs=0.01)


def test_haversine_known_distance():
    result = haversine(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3900 < result < 4000


def _make_txn_df(rows):
    return pd.DataFrame(rows)


def test_compute_features_returns_17_columns():
    df = _make_txn_df([
        {
            "transaction_id": "t1",
            "user_id": "u1",
            "amount": 100.0,
            "merchant_id": "m1",
            "merchant_category": "grocery",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 10:00:00",
            "is_fraud": 0,
        },
        {
            "transaction_id": "t2",
            "user_id": "u1",
            "amount": 200.0,
            "merchant_id": "m2",
            "merchant_category": "dining",
            "location_lat": 40.1,
            "location_lon": -74.1,
            "timestamp": "2024-01-01 11:00:00",
            "is_fraud": 0,
        },
    ])
    result_df, feature_cols = compute_features(df)
    assert len(feature_cols) == 17
    assert len(result_df) == 2


def test_compute_features_has_amount_zscore():
    df = _make_txn_df([
        {
            "transaction_id": "t1",
            "user_id": "u1",
            "amount": 100.0,
            "merchant_id": "m1",
            "merchant_category": "grocery",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 10:00:00",
            "is_fraud": 0,
        },
        {
            "transaction_id": "t2",
            "user_id": "u1",
            "amount": 500.0,
            "merchant_id": "m2",
            "merchant_category": "grocery",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 12:00:00",
            "is_fraud": 0,
        },
    ])
    result_df, _ = compute_features(df)
    assert "amount_zscore" in result_df.columns
    zscores = result_df["amount_zscore"].values
    assert zscores[0] < zscores[1]


def test_compute_features_time_features():
    df = _make_txn_df([
        {
            "transaction_id": "t1",
            "user_id": "u1",
            "amount": 100.0,
            "merchant_id": "m1",
            "merchant_category": "grocery",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-06 15:00:00",
            "is_fraud": 0,
        },
    ])
    result_df, _ = compute_features(df)
    assert result_df.iloc[0]["hour_of_day"] == 15
    assert result_df.iloc[0]["is_weekend"] == 1
    assert result_df.iloc[0]["day_of_week"] == 5


def test_category_map_has_expected_categories():
    assert "grocery" in CATEGORY_MAP
    assert "wire_transfer" in CATEGORY_MAP
    assert "gaming" in CATEGORY_MAP
    assert len(CATEGORY_MAP) == 10


def test_single_transaction_features_no_history():
    txn = {
        "transaction_id": "t1",
        "user_id": "u1",
        "amount": 500.0,
        "merchant_category": "wire_transfer",
        "location_lat": 40.0,
        "location_lon": -74.0,
        "timestamp": "2024-01-15 14:30:00",
    }
    features, cols = compute_single_transaction_features(txn)
    assert features.shape == (1, 17)
    assert len(cols) == 17


def test_single_transaction_features_with_history(sample_user_history):
    txn = {
        "transaction_id": "t1",
        "user_id": "u1",
        "amount": 500.0,
        "merchant_category": "dining",
        "location_lat": 40.72,
        "location_lon": -74.00,
        "timestamp": "2024-06-15T14:30:00",
    }
    features, cols = compute_single_transaction_features(txn, sample_user_history)
    assert features.shape == (1, 17)
    assert features[0][cols.index("is_new_merchant")] == 1


def test_round_amount_detection():
    df = _make_txn_df([
        {
            "transaction_id": "t1",
            "user_id": "u1",
            "amount": 500.0,
            "merchant_id": "m1",
            "merchant_category": "retail",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 10:00:00",
            "is_fraud": 0,
        },
        {
            "transaction_id": "t2",
            "user_id": "u1",
            "amount": 73.45,
            "merchant_id": "m2",
            "merchant_category": "retail",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 11:00:00",
            "is_fraud": 0,
        },
    ])
    result_df, _ = compute_features(df)
    assert result_df.iloc[0]["is_round_amount"] == 1
    assert result_df.iloc[1]["is_round_amount"] == 0


def test_high_risk_category_flag():
    df = _make_txn_df([
        {
            "transaction_id": "t1",
            "user_id": "u1",
            "amount": 100.0,
            "merchant_id": "m1",
            "merchant_category": "wire_transfer",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 10:00:00",
            "is_fraud": 0,
        },
        {
            "transaction_id": "t2",
            "user_id": "u1",
            "amount": 50.0,
            "merchant_id": "m2",
            "merchant_category": "grocery",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": "2024-01-01 11:00:00",
            "is_fraud": 0,
        },
    ])
    result_df, _ = compute_features(df)
    assert result_df.iloc[0]["is_high_risk_category"] == 1
    assert result_df.iloc[1]["is_high_risk_category"] == 0
