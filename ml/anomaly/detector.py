from sklearn.ensemble import IsolationForest

from anomaly.features import OperationalFeatures


class AnomalyDetector:
    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

        self._fitted = False

    def fit(
        self,
        samples: list[OperationalFeatures],
    ) -> None:
        if not samples:
            raise ValueError(
                "At least one training sample is required."
            )

        X = [
            sample.to_vector()
            for sample in samples
        ]

        self.model.fit(X)
        self._fitted = True

    def predict(
        self,
        features: OperationalFeatures,
    ) -> dict:
        if not self._fitted:
            raise RuntimeError(
                "AnomalyDetector must be fitted before prediction."
            )

        X = [
            features.to_vector()
        ]

        prediction = self.model.predict(X)[0]
        score = self.model.decision_function(X)[0]

        return {
            "is_anomaly": bool(prediction == -1),
            "anomaly_score": float(score),
        }