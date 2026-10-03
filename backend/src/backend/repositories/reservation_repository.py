from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Reservation


def list_reservations(db: Session) -> list[Reservation]:
    statement = select(Reservation).order_by(
        Reservation.start_time
    )
    return list(db.scalars(statement).all())


def get_reservation(
    db: Session,
    reservation_id: int,
) -> Reservation | None:
    statement = select(Reservation).where(
        Reservation.id == reservation_id
    )
    return db.scalar(statement)

def find_conflicting_reservations(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
) -> list[Reservation]:
    statement = (
        select(Reservation)
        .where(
            Reservation.room_id == room_id,
            Reservation.status == "ACTIVE",
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
        )
        .order_by(Reservation.start_time)
    )

    return list(db.scalars(statement).all())