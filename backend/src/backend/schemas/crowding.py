from pydantic import BaseModel, Field

from backend.schemas.incident import IncidentRead


class CrowdingObservationCreate(BaseModel):
    event_id: int
    room_id: int
    observed_occupancy: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)


class CrowdingObservationRead(BaseModel):
    event_id: int
    room_id: int
    room_capacity: int
    observed_occupancy: int
    occupancy_ratio: float
    crowding: bool
    incident: IncidentRead | None
    incident_created: bool