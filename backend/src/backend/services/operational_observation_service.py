from sqlalchemy.orm import Session

from backend.models import OperationalObservation

from backend.repositories.operational_observation_repository import (
    create_observation,
    list_observations_for_event,
    get_latest_observation,
)

from backend.services.event_service import (
    get_event,
)


def record_observation(
    db: Session,
    *,
    event_id: int,
    occupancy_ratio: float,
    queue_length: float,
    event_delay_minutes: float,
    vendor_delay_minutes: float,
    equipment_failure_count: int,
    source: str,
) -> OperationalObservation:

    event = get_event(
        db,
        event_id,
    )

    if event is None:
        raise ValueError(
            "Event not found."
        )

    if occupancy_ratio < 0:
        raise ValueError(
            "Occupancy ratio cannot be negative."
        )

    if queue_length < 0:
        raise ValueError(
            "Queue length cannot be negative."
        )

    if event_delay_minutes < 0:
        raise ValueError(
            "Event delay cannot be negative."
        )

    if vendor_delay_minutes < 0:
        raise ValueError(
            "Vendor delay cannot be negative."
        )

    if equipment_failure_count < 0:
        raise ValueError(
            "Equipment failure count cannot be negative."
        )

    observation = OperationalObservation(
        event_id=event_id,
        occupancy_ratio=occupancy_ratio,
        queue_length=queue_length,
        event_delay_minutes=event_delay_minutes,
        vendor_delay_minutes=vendor_delay_minutes,
        equipment_failure_count=equipment_failure_count,
        source=source,
    )

    return create_observation(
        db,
        observation,
    )


def list_event_observations(
    db: Session,
    event_id: int,
) -> list[OperationalObservation]:

    return list_observations_for_event(
        db,
        event_id,
    )


def latest_event_observation(
    db: Session,
    event_id: int,
) -> OperationalObservation | None:

    return get_latest_observation(
        db,
        event_id,
    )