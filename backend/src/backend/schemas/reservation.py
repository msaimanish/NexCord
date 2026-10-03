from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReservationRead(BaseModel):
    id: int
    event_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)