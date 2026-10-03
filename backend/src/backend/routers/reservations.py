from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.dependencies import get_db
from backend.schemas.reservation import ReservationRead
from backend.services.reservation_service import (
    get_reservation,
    list_reservations,
    find_conflicting_reservations,
)


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)


@router.get(
    "",
    response_model=list[ReservationRead],
)
def get_reservations(
    db: Session = Depends(get_db),
):
    return list_reservations(db)

@router.get(
    "/conflicts",
    response_model=list[ReservationRead],
)
def get_reservation_conflicts(
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
):
    try:
        return find_conflicting_reservations(
            db,
            room_id,
            start_time,
            end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/{reservation_id}",
    response_model=ReservationRead,
)
def get_reservation_by_id(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = get_reservation(
        db,
        reservation_id,
    )

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found",
        )

    return reservation