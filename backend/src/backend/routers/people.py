from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.dependencies import get_db
from backend.schemas.person import (
    PersonAvailabilityRead,
    PersonRead,
)
from backend.services.person_service import (
    check_person_availability,
    get_person,
    list_people,
)


router = APIRouter(
    prefix="/people",
    tags=["People"],
)


@router.get(
    "",
    response_model=list[PersonRead],
)
def get_people(
    db: Session = Depends(get_db),
):
    return list_people(db)

@router.get(
    "/{person_id}/availability",
    response_model=PersonAvailabilityRead,
)
def get_person_availability(
    person_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
):
    try:
        result = check_person_availability(
            db,
            person_id,
            start_time,
            end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return result

@router.get(
    "/{person_id}",
    response_model=PersonRead,
)
def get_person_by_id(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = get_person(
        db,
        person_id,
    )

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return person