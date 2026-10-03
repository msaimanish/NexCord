from pydantic import BaseModel
from backend.schemas.event import EventRead
from backend.schemas.incident import (
    EventEquipmentContext,
    EventPersonContext,
    EventVendorContext,
    IncidentRead,
)
from backend.schemas.reservation import ReservationRead
from backend.schemas.room import RoomRead


class ReservationContext(BaseModel):
    reservation: ReservationRead
    room: RoomRead


class OperationalStateRead(BaseModel):
    event: EventRead

    reservations: list[ReservationContext]
    conflicting_reservations: list[ReservationRead]

    incidents: list[IncidentRead]

    assigned_people: list[EventPersonContext]
    assigned_vendors: list[EventVendorContext]
    assigned_equipment: list[EventEquipmentContext]

    open_incident_count: int
    state_facts: list[str]