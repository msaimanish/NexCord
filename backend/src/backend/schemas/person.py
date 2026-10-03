from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PersonRead(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    role: str

    model_config = ConfigDict(from_attributes=True)

class PersonAssignmentConflictRead(BaseModel):
    event_id: int
    event_name: str
    assignment_role: str
    start_time: datetime
    end_time: datetime


class PersonAvailabilityRead(BaseModel):
    person_id: int
    requested_start: datetime
    requested_end: datetime
    available: bool
    reason: str
    conflicts: list[PersonAssignmentConflictRead]