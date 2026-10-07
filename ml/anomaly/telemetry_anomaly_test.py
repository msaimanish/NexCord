from anomaly.detector import AnomalyDetector
from anomaly.telemetry_adapter import (
    get_latest_features,
)
from anomaly.test_anomaly import (
    generate_normal_samples,
)


def main() -> None:
    detector = AnomalyDetector(
        contamination=0.05,
    )

    training_samples = (
        generate_normal_samples()
    )

    detector.fit(
        training_samples
    )

    features = get_latest_features(
        event_id=3,
    )

    result = detector.predict(
        features
    )

    print("Real telemetry:")
    print(features)

    print()
    print("Anomaly result:")
    print(result)


if __name__ == "__main__":
    main()