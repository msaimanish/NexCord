from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.dependencies import get_db

from backend.schemas.operational_observation import (
    OperationalObservationCreate,
    OperationalObservationRead,
)

from backend.services.operational_observation_service import (
    record_observation,
    list_event_observations,
    latest_event_observation,
)


router = APIRouter(
    prefix="/operational-observations",
    tags=["Operational Observations"],
)


@router.post(
    "",
    response_model=OperationalObservationRead,
)
def create_operational_observation(
    payload: OperationalObservationCreate,
    db: Session = Depends(get_db),
):
    try:
        observation = record_observation(
            db,
            event_id=payload.event_id,
            occupancy_ratio=payload.occupancy_ratio,
            queue_length=payload.queue_length,
            event_delay_minutes=payload.event_delay_minutes,
            vendor_delay_minutes=payload.vendor_delay_minutes,
            equipment_failure_count=(
                payload.equipment_failure_count
            ),
            source=payload.source,
        )

        db.commit()
        db.refresh(observation)

        return observation

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/event/{event_id}",
    response_model=list[OperationalObservationRead],
)
def get_operational_observations(
    event_id: int,
    db: Session = Depends(get_db),
):
    return list_event_observations(
        db,
        event_id,
    )


@router.get(
    "/event/{event_id}/latest",
    response_model=OperationalObservationRead,
)
def get_latest_operational_observation(
    event_id: int,
    db: Session = Depends(get_db),
):
    observation = latest_event_observation(
        db,
        event_id,
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail="No operational observations found.",
        )

    return observation