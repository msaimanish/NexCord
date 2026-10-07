import httpx

from anomaly.features import OperationalFeatures


def get_latest_features(
    event_id: int,
    base_url: str = "http://127.0.0.1:8000",
) -> OperationalFeatures:
    url = (
        f"{base_url}"
        f"/api/v1/operational-observations"
        f"/event/{event_id}/latest"
    )

    response = httpx.get(
        url,
        timeout=10.0,
    )

    response.raise_for_status()

    observation = response.json()

    return OperationalFeatures(
        occupancy_ratio=observation[
            "occupancy_ratio"
        ],
        queue_length=observation[
            "queue_length"
        ],
        event_delay_minutes=observation[
            "event_delay_minutes"
        ],
        vendor_delay_minutes=observation[
            "vendor_delay_minutes"
        ],
        equipment_failure_count=float(
            observation[
                "equipment_failure_count"
            ]
        ),
    )