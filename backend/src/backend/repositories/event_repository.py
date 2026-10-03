from sqlalchemy import select

from sqlalchemy.orm import Session, aliased

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


def list_events(db: Session) -> list[Event]:
    statement = select(Event).order_by(Event.start_time)
    return list(db.scalars(statement).all())


def get_event(db: Session, event_id: int) -> Event | None:
    statement = select(Event).where(Event.id == event_id)
    return db.scalar(statement)

def get_event_operational_state(
    db: Session,
    event_id: int,
) -> dict | None:
    event = get_event(db, event_id)

    if event is None:
        return None

    reservations = list(
        db.scalars(
            select(Reservation)
            .where(
                Reservation.event_id == event_id,
                Reservation.status == "ACTIVE",
            )
            .order_by(Reservation.start_time)
        ).all()
    )

    reservation_context = []

    for reservation in reservations:
        room = db.scalar(
            select(Room).where(
                Room.id == reservation.room_id
            )
        )

        if room is not None:
            reservation_context.append(
                {
                    "reservation": reservation,
                    "room": room,
                }
            )

    target = aliased(Reservation)

    conflicting_reservations = list(
        db.scalars(
            select(Reservation)
            .join(
                target,
                Reservation.room_id == target.room_id,
            )
            .where(
                target.event_id == event_id,
                target.status == "ACTIVE",
                Reservation.status == "ACTIVE",
                Reservation.event_id != event_id,
                Reservation.start_time < target.end_time,
                Reservation.end_time > target.start_time,
            )
            .distinct()
            .order_by(Reservation.start_time)
        ).all()
    )

    incidents = list(
        db.scalars(
            select(Incident)
            .where(
                Incident.event_id == event_id
            )
            .order_by(Incident.detected_at.desc())
        ).all()
    )

    people = list(
        db.execute(
            select(
                Person,
                EventPerson.assignment_role,
            )
            .join(
                EventPerson,
                EventPerson.person_id == Person.id,
            )
            .where(
                EventPerson.event_id == event_id
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
                EventVendor.event_id == event_id
            )
            .order_by(Vendor.name)
        ).all()
    )

    equipment = list(
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
                EventEquipment.event_id == event_id
            )
            .order_by(Equipment.name)
        ).all()
    )

    return {
        "event": event,
        "reservations": reservation_context,
        "conflicting_reservations": conflicting_reservations,
        "incidents": incidents,
        "people": people,
        "vendors": vendors,
        "equipment": equipment,
    }