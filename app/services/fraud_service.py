import json
import os

import joblib
import numpy as np

from app.ml.explainer import FraudExplainer
from app.ml.feature_engineering import (
    compute_single_transaction_features,
    load_feature_columns,
)


class FraudDetectionService:
    def __init__(self, model_path="models/"):
        self.model_path = model_path
        self.iso_forest = joblib.load(os.path.join(model_path, "isolation_forest.joblib"))
        self.lgbm_model = joblib.load(os.path.join(model_path, "lightgbm_model.joblib"))
        self.feature_columns = load_feature_columns(model_path)
        self.explainer = FraudExplainer(self.lgbm_model)

    def predict(self, transaction_dict, user_history=None):
        features, feature_names = compute_single_transaction_features(
            transaction_dict, user_history
        )

        iso_score = self.iso_forest.decision_function(features)[0]
        iso_anomaly = self.iso_forest.predict(features)[0]

        lgbm_proba = float(self.lgbm_model.predict_proba(features)[0][1])

        combined_score = lgbm_proba
        if iso_anomaly == -1:
            combined_score = min(combined_score + 0.15, 1.0)

        risk_tier = self._get_risk_tier(combined_score)

        explanation = self.explainer.explain(features, feature_names)

        action = self._recommend_action(risk_tier)

        return {
            "fraud_probability": round(combined_score, 4),
            "risk_tier": risk_tier,
            "iso_forest_score": round(float(iso_score), 4),
            "lgbm_probability": round(lgbm_proba, 4),
            "top_features": explanation["top_features"],
            "all_shap_values": explanation["all_shap_values"],
            "recommended_action": action,
        }

    def _get_risk_tier(self, probability):
        if probability >= 0.8:
            return "critical"
        elif probability >= 0.5:
            return "high"
        elif probability >= 0.2:
            return "medium"
        return "low"

    def _recommend_action(self, risk_tier):
        actions = {
            "critical": "block_transaction",
            "high": "require_verification",
            "medium": "flag_for_review",
            "low": "approve",
        }
        return actions.get(risk_tier, "approve")
