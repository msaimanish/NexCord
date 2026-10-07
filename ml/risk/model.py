from xgboost import XGBClassifier

from risk.features import RiskFeatures


class IncidentRiskPredictor:
    def __init__(self) -> None:
        self.model = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
        )

        self._fitted = False

    def fit(
        self,
        samples: list[RiskFeatures],
        labels: list[int],
    ) -> None:
        if not samples:
            raise ValueError(
                "Training samples cannot be empty."
            )

        if len(samples) != len(labels):
            raise ValueError(
                "Samples and labels must have "
                "the same length."
            )

        X = [
            sample.to_vector()
            for sample in samples
        ]

        self.model.fit(
            X,
            labels,
        )

        self._fitted = True

    def predict(
        self,
        features: RiskFeatures,
    ) -> dict:
        if not self._fitted:
            raise RuntimeError(
                "Model must be fitted before prediction."
            )

        X = [features.to_vector()]

        probability = (
            self.model.predict_proba(X)[0][1]
        )

        prediction = self.model.predict(X)[0]

        return {
            "incident_probability": float(
                probability
            ),
            "is_high_risk": bool(
                prediction == 1
            ),
        }