import httpx

from anomaly.detector import AnomalyDetector
from anomaly.state_adapter import event_state_to_features
from anomaly.test_anomaly import generate_normal_samples


API_URL = "http://127.0.0.1:8000/api/v1/events/3/state"


def main() -> None:
    detector = AnomalyDetector(
        contamination=0.05,
    )

    detector.fit(
        generate_normal_samples()
    )

    response = httpx.get(
        API_URL,
        timeout=10.0,
    )

    response.raise_for_status()

    event_state = response.json()

    features = event_state_to_features(
        event_state
    )

    result = detector.predict(
        features
    )

    print("Real Robotics state:")
    print(features)

    print()
    print("Anomaly result:")
    print(result)


if __name__ == "__main__":
    main()