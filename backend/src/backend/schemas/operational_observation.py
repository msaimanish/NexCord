from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class OperationalObservationCreate(BaseModel):
    event_id: int

    occupancy_ratio: float = Field(
        ge=0.0,
    )

    queue_length: float = Field(
        ge=0.0,
    )

    event_delay_minutes: float = Field(
        ge=0.0,
    )

    vendor_delay_minutes: float = Field(
        ge=0.0,
    )

    equipment_failure_count: int = Field(
        ge=0,
    )

    source: str = Field(
        min_length=1,
        max_length=50,
    )


class OperationalObservationRead(BaseModel):
    id: int
    event_id: int
    observed_at: datetime
    occupancy_ratio: float
    queue_length: float
    event_delay_minutes: float
    vendor_delay_minutes: float
    equipment_failure_count: int
    source: str

    model_config = ConfigDict(
        from_attributes=True
    )