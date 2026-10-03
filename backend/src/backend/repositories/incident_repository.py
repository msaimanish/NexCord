from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.models import (
    Equipment,
    Event,
    EventEquipment,
    EventPerson,
    EventVendor,
    Incident,
    Person,
    Reservation,
    Room,
    Vendor,
)

def list_incidents(db: Session) -> list[Incident]:
    statement = select(Incident).order_by(Incident.detected_at.desc())
    return list(db.scalars(statement).all())


def get_incident(
    db: Session,
    incident_id: int,
) -> Incident | None:
    statement = select(Incident).where(
        Incident.id == incident_id
    )
    return db.scalar(statement)

def get_incident_context(
    db: Session,
    incident_id: int,
) -> dict | None:
    incident = get_incident(db, incident_id)

    if incident is None:
        return None

    event = db.scalar(
        select(Event).where(Event.id == incident.event_id)
    )

    if event is None:
        return None

    room = None
    if incident.room_id is not None:
        room = db.scalar(
            select(Room).where(Room.id == incident.room_id)
        )

    vendor = None
    if incident.vendor_id is not None:
        vendor = db.scalar(
            select(Vendor).where(Vendor.id == incident.vendor_id)
        )

    person = None
    if incident.person_id is not None:
        person = db.scalar(
            select(Person).where(Person.id == incident.person_id)
        )

    equipment = None
    if incident.equipment_id is not None:
        equipment = db.scalar(
            select(Equipment).where(
                Equipment.id == incident.equipment_id
            )
        )

    reservations = list(
        db.scalars(
            select(Reservation)
            .where(
                Reservation.event_id == event.id,
                Reservation.status == "ACTIVE",
            )
            .order_by(Reservation.start_time)
        ).all()
    )

    people = list(
        db.execute(
            select(Person, EventPerson.assignment_role)
            .join(
                EventPerson,
                EventPerson.person_id == Person.id,
            )
            .where(
                EventPerson.event_id == event.id
            )
            .order_by(Person.name)
        ).all()
    )

    vendors = list(
        db.execute(
            select(
                Vendor,
                EventVendor.service_type,
                EventVendor.status,
            )
            .join(
                EventVendor,
                EventVendor.vendor_id == Vendor.id,
            )
            .where(
                EventVendor.event_id == event.id
            )
            .order_by(Vendor.name)
        ).all()
    )

    equipment_assignments = list(
        db.execute(
            select(
                Equipment,
                EventEquipment.quantity,
            )
            .join(
                EventEquipment,
                EventEquipment.equipment_id == Equipment.id,
            )
            .where(
                EventEquipment.event_id == event.id
            )
            .order_by(Equipment.name)
        ).all()
    )

    return {
        "incident": incident,
        "event": event,
        "room": room,
        "vendor": vendor,
        "person": person,
        "equipment": equipment,
        "reservations": reservations,
        "people": people,
        "vendors": vendors,
        "equipment_assignments": equipment_assignments,
    }