from risk.state_adapter import (
    build_risk_features,
)


def main() -> None:
    features = build_risk_features(
        event_id=3,
    )

    print("Robotics risk features:")
    print(features)

    print()
    print("Vector:")
    print(features.to_vector())


if __name__ == "__main__":
    main()