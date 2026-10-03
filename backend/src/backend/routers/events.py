from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.schemas.event import EventRead
from backend.services.event_service import (
    get_event,
    list_events,
    get_event_operational_state,
)
from backend.schemas.event_state import OperationalStateRead

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("", response_model=list[EventRead])
def get_events(
    db: Session = Depends(get_db),
):
    return list_events(db)

@router.get(
    "/{event_id}/state",
    response_model=OperationalStateRead,
)
def get_event_state(
    event_id: int,
    db: Session = Depends(get_db),
):
    state = get_event_operational_state(
        db,
        event_id,
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return state

@router.get("/{event_id}", response_model=EventRead)
def get_event_by_id(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = get_event(db, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return event