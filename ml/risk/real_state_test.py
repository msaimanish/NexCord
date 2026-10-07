from risk.model import IncidentRiskPredictor
from risk.state_adapter import build_risk_features
from risk.test_risk import generate_dataset


def main() -> None:
    samples, labels = generate_dataset()

    predictor = IncidentRiskPredictor()

    predictor.fit(
        samples,
        labels,
    )

    features = build_risk_features(
        event_id=3,
    )

    result = predictor.predict(
        features
    )

    print("Real Robotics risk features:")
    print(features)

    print()
    print("Incident risk prediction:")
    print(result)


if __name__ == "__main__":
    main()