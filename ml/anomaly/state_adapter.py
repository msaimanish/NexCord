from anomaly.features import OperationalFeatures


def event_state_to_features(
    event_state: dict,
) -> OperationalFeatures:
    incidents = event_state.get(
        "incidents",
        [],
    )

    occupancy_ratio = 0.0

    equipment_failure_count = 0.0

    for incident in incidents:
        if incident.get("type") == "CROWDING":
            extra_data = incident.get(
                "extra_data",
                {},
            )

            observed = extra_data.get(
                "observed_occupancy"
            )

            capacity = extra_data.get(
                "room_capacity"
            )

            if (
                observed is not None
                and capacity is not None
                and capacity > 0
            ):
                occupancy_ratio = max(
                    occupancy_ratio,
                    observed / capacity,
                )

        if incident.get("type") == "EQUIPMENT_FAILURE":
            equipment_failure_count += 1

    return OperationalFeatures(
        occupancy_ratio=occupancy_ratio,
        queue_length=0.0,
        event_delay_minutes=0.0,
        vendor_delay_minutes=0.0,
        equipment_failure_count=equipment_failure_count,
    )