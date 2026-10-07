from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.incident import (
    IncidentImpactRead,
    IncidentRead,
)
from backend.dependencies import get_db
from backend.services.incident_service import (
    analyze_incident_impact,
    get_incident,
    list_incidents,
    record_crowding_observation,
)
from backend.schemas.crowding import (
    CrowdingObservationCreate,
    CrowdingObservationRead,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.get(
    "",
    response_model=list[IncidentRead],
)
def get_incidents(
    db: Session = Depends(get_db),
):
    return list_incidents(db)

@router.post(
    "/crowding",
    response_model=CrowdingObservationRead,
)
def record_crowding(
    request: CrowdingObservationCreate,
    db: Session = Depends(get_db),
):
    try:
        return record_crowding_observation(
            db,
            request.event_id,
            request.room_id,
            request.observed_occupancy,
            request.confidence,
        )

    except ValueError as exc:
        message = str(exc)

        if message in {
            "Event not found",
            "Room not found",
        }:
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )

@router.get(
    "/{incident_id}/impact",
    response_model=IncidentImpactRead,
)
def get_incident_impact(
    incident_id: int,
    db: Session = Depends(get_db),
):
    result = analyze_incident_impact(
        db,
        incident_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return result

@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident