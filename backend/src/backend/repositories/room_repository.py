from sqlalchemy import select, exists
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Reservation, Room


def list_rooms(db: Session) -> list[Room]:
    statement = select(Room).order_by(Room.name)
    return list(db.scalars(statement).all())


def get_room(db: Session, room_id: int) -> Room | None:
    statement = select(Room).where(Room.id == room_id)
    return db.scalar(statement)

def find_available_rooms(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    required_capacity: int,
) -> list[Room]:
    reservation_conflict = exists().where(
        Reservation.room_id == Room.id,
        Reservation.status == "ACTIVE",
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )

    statement = (
        select(Room)
        .where(
            Room.status == "AVAILABLE",
            Room.capacity >= required_capacity,
            ~reservation_conflict,
        )
        .order_by(Room.capacity, Room.name)
    )

    return list(db.scalars(statement).all())