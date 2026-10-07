from anomaly.telemetry_adapter import (
    get_latest_features,
)


def main() -> None:
    features = get_latest_features(
        event_id=3,
    )

    print("Latest Robotics telemetry:")
    print(features)

    print()
    print("Feature vector:")
    print(features.to_vector())


if __name__ == "__main__":
    main()