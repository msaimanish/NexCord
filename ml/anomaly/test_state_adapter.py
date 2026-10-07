import httpx

from anomaly.state_adapter import event_state_to_features


API_URL = "http://127.0.0.1:8000/api/v1/events/3/state"


def main() -> None:
    response = httpx.get(
        API_URL,
        timeout=10.0,
    )

    response.raise_for_status()

    event_state = response.json()

    features = event_state_to_features(
        event_state
    )

    print("Operational features:")
    print(features)

    print("Vector:")
    print(features.to_vector())


if __name__ == "__main__":
    main()