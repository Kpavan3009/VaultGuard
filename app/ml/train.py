import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.ml.feature_engineering import compute_features


def main():
    df = pd.read_csv("data/transactions.csv")
    print(f"loaded {len(df)} transactions")

    df_featured, feature_columns = compute_features(df)
    print(f"computed {len(feature_columns)} features")

    X = df_featured[feature_columns].values
    y = df_featured["is_fraud"].values

    print("training isolation forest...")
    iso_forest = IsolationForest(
        contamination=0.005,
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    iso_forest.fit(X)
    iso_scores = iso_forest.decision_function(X)
    print(f"isolation forest trained, score range: [{iso_scores.min():.4f}, {iso_scores.max():.4f}]")

    fraud_ratio = y.sum() / len(y)
    scale_weight = (1 - fraud_ratio) / max(fraud_ratio, 1e-6)
    print(f"fraud ratio: {fraud_ratio:.4f}, scale_pos_weight: {scale_weight:.1f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("training lightgbm classifier...")
    lgbm_model = lgb.LGBMClassifier(
        num_leaves=31,
        learning_rate=0.05,
        n_estimators=300,
        is_unbalance=True,
        random_state=42,
        verbose=-1,
    )
    lgbm_model.fit(X_train, y_train)

    y_pred_proba = lgbm_model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\nauc: {auc:.4f}")
    print(f"precision: {precision:.4f}")
    print(f"recall: {recall:.4f}")
    print(f"f1: {f1:.4f}")
    print(f"confusion matrix:\n{cm}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(iso_forest, "models/isolation_forest.joblib")
    joblib.dump(lgbm_model, "models/lightgbm_model.joblib")

    with open("models/feature_columns.json", "w") as f:
        json.dump(feature_columns, f)

    print("\nmodels saved to models/")


if __name__ == "__main__":
    main()
