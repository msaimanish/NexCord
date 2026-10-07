from datetime import datetime, timezone

import httpx

from risk.features import RiskFeatures


BASE_URL = "http://127.0.0.1:8000"


def _get(
    path: str,
) -> dict | list:
    response = httpx.get(
        f"{BASE_URL}{path}",
        timeout=10.0,
    )

    response.raise_for_status()

    return response.json()


def build_risk_features(
    event_id: int,
) -> RiskFeatures:

    event = _get(
        f"/api/v1/events/{event_id}"
    )

    observation = _get(
        f"/api/v1/operational-observations"
        f"/event/{event_id}/latest"
    )

    event_state = _get(
        f"/api/v1/events/{event_id}/state"
    )

    incidents = event_state.get(
        "incidents",
        [],
    )

    assigned_people = event_state.get(
        "assigned_people",
        [],
    )

    assigned_vendors = event_state.get(
        "assigned_vendors",
        [],
    )

    assigned_equipment = event_state.get(
        "assigned_equipment",
        [],
    )

    # --------------------------------------------------
    # 1. Current occupancy
    # --------------------------------------------------

    current_occupancy = float(
        observation["occupancy_ratio"]
    )

    # --------------------------------------------------
    # 2. Event size
    # --------------------------------------------------

    event_size = float(
        event["expected_attendees"]
    )

    # --------------------------------------------------
    # 3. Time remaining
    # --------------------------------------------------

    observed_at = datetime.fromisoformat(
        observation["observed_at"].replace(
            "Z",
            "+00:00",
        )
    )

    event_end = datetime.fromisoformat(
        event["end_time"].replace(
            "Z",
            "+00:00",
        )
    )

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )

    if event_end.tzinfo is None:
        event_end = event_end.replace(
            tzinfo=timezone.utc
        )

    time_remaining_minutes = max(
        0.0,
        min(
            180.0,
            (
                event_end - observed_at
            ).total_seconds() / 60.0,
        ),
    )
    # --------------------------------------------------
    # 4. Vendor reliability
    # --------------------------------------------------

    reliability_values = []

    for vendor_entry in assigned_vendors:
        vendor = vendor_entry["vendor"]

        reliability = vendor.get(
            "reliability_score"
        )

        if reliability is not None:
            reliability_values.append(
                float(reliability)
            )

    if reliability_values:
        vendor_reliability = min(
            reliability_values
        )
    else:
        vendor_reliability = 1.0

    # --------------------------------------------------
    # 5. Staff availability
    # --------------------------------------------------

    staff_count = len(
        assigned_people
    )

    unavailable_staff_ids = {
        incident["person_id"]
        for incident in incidents
        if (
            incident["type"]
            == "PERSON_UNAVAILABLE"
            and incident["person_id"] is not None
        )
    }

    if staff_count > 0:
        unavailable_count = sum(
            1
            for person_entry in assigned_people
            if person_entry["person"]["id"]
            in unavailable_staff_ids
        )

        staff_availability = max(
            0.0,
            1.0
            - (
                unavailable_count
                / staff_count
            ),
        )
    else:
        staff_availability = 1.0

    # --------------------------------------------------
    # 6. Equipment status
    # --------------------------------------------------

    equipment_count = len(
        assigned_equipment
    )

    failed_equipment_ids = {
        incident["equipment_id"]
        for incident in incidents
        if (
            incident["type"]
            == "EQUIPMENT_FAILURE"
            and incident["equipment_id"] is not None
        )
    }

    if equipment_count > 0:
        failed_count = sum(
            1
            for equipment_entry in assigned_equipment
            if equipment_entry["equipment"]["id"]
            in failed_equipment_ids
        )

        equipment_status = max(
            0.0,
            1.0
            - (
                failed_count
                / equipment_count
            ),
        )
    else:
        equipment_status = 1.0

    # --------------------------------------------------
    # 7. Historical incidents
    # --------------------------------------------------

    historical_incidents = float(
        sum(
            1
            for incident in incidents
            if datetime.fromisoformat(
                incident["detected_at"].replace(
                    "Z",
                    "+00:00",
                )
            ) < observed_at
        )
    )

    return RiskFeatures(
        current_occupancy=current_occupancy,
        event_size=event_size,
        time_remaining_minutes=(
            time_remaining_minutes
        ),
        vendor_reliability=(
            vendor_reliability
        ),
        staff_availability=(
            staff_availability
        ),
        equipment_status=(
            equipment_status
        ),
        historical_incidents=(
            historical_incidents
        ),
    )