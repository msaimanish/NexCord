from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.dependencies import get_db
from backend.schemas.room import RoomRead
from backend.services.room_service import (
    get_room,
    list_rooms,
    find_available_rooms,
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


@router.get("", response_model=list[RoomRead])
def get_rooms(
    db: Session = Depends(get_db),
):
    return list_rooms(db)

@router.get(
    "/available",
    response_model=list[RoomRead],
)
def get_available_rooms(
    start_time: datetime,
    end_time: datetime,
    required_capacity: int,
    db: Session = Depends(get_db),
):
    try:
        return find_available_rooms(
            db,
            start_time,
            end_time,
            required_capacity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get("/{room_id}", response_model=RoomRead)
def get_room_by_id(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = get_room(db, room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    return room