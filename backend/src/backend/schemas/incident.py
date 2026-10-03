from datetime import datetime

from pydantic import BaseModel, ConfigDict
from backend.schemas.equipment import EquipmentRead
from backend.schemas.event import EventRead
from backend.schemas.person import PersonRead
from backend.schemas.reservation import ReservationRead
from backend.schemas.room import RoomRead
from backend.schemas.vendor import VendorRead

class IncidentRead(BaseModel):
    id: int
    event_id: int

    room_id: int | None
    vendor_id: int | None
    person_id: int | None
    equipment_id: int | None

    type: str
    severity: str
    status: str
    source: str

    title: str
    description: str | None

    extra_data: dict | None

    detected_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class EventPersonContext(BaseModel):
    person: PersonRead
    assignment_role: str


class EventVendorContext(BaseModel):
    vendor: VendorRead
    service_type: str
    status: str


class EventEquipmentContext(BaseModel):
    equipment: EquipmentRead
    quantity: int


class IncidentImpactRead(BaseModel):
    incident: IncidentRead
    event: EventRead

    affected_room: RoomRead | None
    affected_vendor: VendorRead | None
    affected_person: PersonRead | None
    affected_equipment: EquipmentRead | None

    active_reservations: list[ReservationRead]
    conflicting_reservations: list[ReservationRead]

    assigned_people: list[EventPersonContext]
    assigned_vendors: list[EventVendorContext]
    assigned_equipment: list[EventEquipmentContext]

    impact_facts: list[str]