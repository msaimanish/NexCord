from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.incident import (
    IncidentImpactRead,
    IncidentRead,
)
from backend.dependencies import get_db
from backend.services.incident_service import (
    get_incident,
    list_incidents,
    analyze_incident_impact,
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