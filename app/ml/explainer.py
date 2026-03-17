import numpy as np
import shap


class FraudExplainer:
    def __init__(self, model):
        self.explainer = shap.TreeExplainer(model)

    def explain(self, features, feature_names):
        shap_values = self.explainer.shap_values(features)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        if shap_values.ndim == 1:
            values = shap_values
        else:
            values = shap_values[0]

        feature_importance = []
        for i, name in enumerate(feature_names):
            feature_importance.append({
                "feature": name,
                "shap_value": float(values[i]),
                "abs_impact": float(abs(values[i])),
            })

        feature_importance.sort(key=lambda x: x["abs_impact"], reverse=True)
        top_features = feature_importance[:3]

        return {
            "top_features": top_features,
            "all_shap_values": {name: float(values[i]) for i, name in enumerate(feature_names)},
        }
