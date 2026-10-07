from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventRead(BaseModel):
    id: int
    name: str
    description: str | None
    start_time: datetime
    end_time: datetime
    status: str
    expected_attendees: int
    model_config = ConfigDict(from_attributes=True)