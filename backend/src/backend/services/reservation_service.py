from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Reservation
from backend.repositories.reservation_repository import (
    get_reservation as repository_get_reservation,
    list_reservations as repository_list_reservations,
    find_conflicting_reservations as repository_find_conflicting_reservations,
)


def list_reservations(db: Session) -> list[Reservation]:
    return repository_list_reservations(db)


def get_reservation(
    db: Session,
    reservation_id: int,
) -> Reservation | None:
    return repository_get_reservation(
        db,
        reservation_id,
    )

def find_conflicting_reservations(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
) -> list[Reservation]:
    if start_time >= end_time:
        raise ValueError(
            "start_time must be earlier than end_time"
        )

    return repository_find_conflicting_reservations(
        db,
        room_id,
        start_time,
        end_time,
    )

