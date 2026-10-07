import random

from risk.features import RiskFeatures


def generate_dataset(
    count: int = 2000,
) -> tuple[list[RiskFeatures], list[int]]:
    random.seed(42)

    samples = []
    labels = []

    for _ in range(count):
        features = RiskFeatures(
            current_occupancy=random.uniform(
                0.3,
                1.3,
            ),
            event_size=random.uniform(
                20,
                500,
            ),
            time_remaining_minutes=random.uniform(
                0,
                180,
            ),
            vendor_reliability=random.uniform(
                0.4,
                1.0,
            ),
            staff_availability=random.uniform(
                0.4,
                1.0,
            ),
            equipment_status=random.uniform(
                0.4,
                1.0,
            ),
            historical_incidents=random.uniform(
                0,
                5,
            ),
        )

        risk_score = (
            features.current_occupancy * 2.5
            + features.event_size / 250
            + (
                180
                - features.time_remaining_minutes
            ) / 180
            + (1 - features.vendor_reliability) * 1.5
            + (1 - features.staff_availability) * 1.5
            + (1 - features.equipment_status) * 1.5
            + features.historical_incidents * 0.4
        )

        risk_score += random.gauss(
            0,
            0.4,
        )

        label = int(
            risk_score > 3.8
        )

        samples.append(features)
        labels.append(label)

    return samples, labels