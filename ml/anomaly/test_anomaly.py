import random

from anomaly.detector import AnomalyDetector
from anomaly.features import OperationalFeatures


def generate_normal_samples(
    count: int = 200,
) -> list[OperationalFeatures]:
    random.seed(42)

    samples = []

    for _ in range(count):
        samples.append(
            OperationalFeatures(
                occupancy_ratio=random.uniform(
                    0.40,
                    0.90,
                ),
                queue_length=random.uniform(
                    0,
                    10,
                ),
                event_delay_minutes=random.uniform(
                    0,
                    5,
                ),
                vendor_delay_minutes=random.uniform(
                    0,
                    5,
                ),
                equipment_failure_count=random.choice(
                    [0, 0, 0, 0, 1]
                ),
            )
        )

    return samples


def main() -> None:
    training_samples = generate_normal_samples()

    detector = AnomalyDetector(
        contamination=0.05,
    )

    detector.fit(
        training_samples
    )

    normal_state = OperationalFeatures(
        occupancy_ratio=0.75,
        queue_length=5,
        event_delay_minutes=2,
        vendor_delay_minutes=3,
        equipment_failure_count=0,
    )

    anomalous_state = OperationalFeatures(
        occupancy_ratio=1.25,
        queue_length=80,
        event_delay_minutes=45,
        vendor_delay_minutes=40,
        equipment_failure_count=4,
    )

    print(
        "Normal:",
        detector.predict(normal_state),
    )

    print(
        "Anomalous:",
        detector.predict(anomalous_state),
    )


if __name__ == "__main__":
    main()