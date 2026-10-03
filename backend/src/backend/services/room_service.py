from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Room
from backend.repositories.room_repository import (
    get_room as repository_get_room,
    list_rooms as repository_list_rooms,
    find_available_rooms as repository_find_available_rooms,
)


def list_rooms(db: Session) -> list[Room]:
    return repository_list_rooms(db)


def get_room(db: Session, room_id: int) -> Room | None:
    return repository_get_room(db, room_id)

def find_available_rooms(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    required_capacity: int,
) -> list[Room]:
    if start_time >= end_time:
        raise ValueError(
            "start_time must be earlier than end_time"
        )

    if required_capacity <= 0:
        raise ValueError(
            "required_capacity must be greater than 0"
        )

    return repository_find_available_rooms(
        db,
        start_time,
        end_time,
        required_capacity,
    )