from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models import Incident
from backend.services.reservation_service import (
    find_conflicting_reservations,
)
from backend.repositories.incident_repository import (
    get_incident as repository_get_incident,
    get_incident_context as repository_get_incident_context,
    list_incidents as repository_list_incidents,
)
from backend.services.event_service import get_event
from backend.services.room_service import get_room
from backend.repositories.incident_repository import (
    create_incident as repository_create_incident,
    find_open_crowding_incident,
)

def list_incidents(db: Session) -> list[Incident]:
    return repository_list_incidents(db)


def get_incident(
    db: Session,
    incident_id: int,
) -> Incident | None:
    return repository_get_incident(db, incident_id)

def analyze_incident_impact(
    db: Session,
    incident_id: int,
) -> dict | None:
    context = repository_get_incident_context(
        db,
        incident_id,
    )

    if context is None:
        return None

    incident = context["incident"]
    event = context["event"]
    event_incidents = list(
        db.scalars(
            select(Incident)
            .where(Incident.event_id == event.id)
            .order_by(Incident.id)
        ).all()
    )
    room = context["room"]
    reservations = context["reservations"]

    conflicting_reservations = []

    if room is not None:
        room_reservation = next(
            (
                reservation
                for reservation in reservations
                if reservation.room_id == room.id
            ),
            None,
        )

        if room_reservation is not None:
            conflicting_reservations = (
                find_conflicting_reservations(
                    db,
                    room.id,
                    room_reservation.start_time,
                    room_reservation.end_time,
                )
            )

            conflicting_reservations = [
                reservation
                for reservation in conflicting_reservations
                if reservation.id != room_reservation.id
            ]

    impact_facts = []

    if room is not None:
        impact_facts.append(
            f"Incident affects room {room.name} "
            f"with capacity {room.capacity}."
        )

    if conflicting_reservations:
        impact_facts.append(
            f"Room has {len(conflicting_reservations)} "
            f"overlapping active reservation(s)."
        )

    if incident.type == "CROWDING" and room is not None:
        observed_occupancy = None

        if incident.extra_data:
            observed_occupancy = incident.extra_data.get(
                "observed_occupancy"
            )

        if (
            observed_occupancy is not None
            and observed_occupancy > room.capacity
        ):
            impact_facts.append(
                f"Observed occupancy of {observed_occupancy} "
                f"exceeds room capacity of {room.capacity}."
            )

    if incident.type == "VENDOR_CANCELLED":
        impact_facts.append(
            "Incident reports cancellation of an assigned vendor."
        )

    if incident.type == "EQUIPMENT_FAILURE":
        impact_facts.append(
            "Incident reports failure of an affected equipment resource."
        )

    if incident.type == "PERSON_UNAVAILABLE":
        impact_facts.append(
            "Incident reports unavailability of an assigned person."
        )

    return {
        "incident": incident,
        "event": event,
        "affected_room": room,
        "affected_vendor": context["vendor"],
        "incidents": event_incidents,
        "affected_person": context["person"],
        "affected_equipment": context["equipment"],
        "active_reservations": reservations,
        "conflicting_reservations": conflicting_reservations,
        "assigned_people": [
            {
                "person": person,
                "assignment_role": assignment_role,
            }
            for person, assignment_role in context["people"]
        ],
        "assigned_vendors": [
            {
                "vendor": vendor,
                "service_type": service_type,
                "status": status,
            }
            for vendor, service_type, status in context["vendors"]
        ],
        "assigned_equipment": [
            {
                "equipment": equipment,
                "quantity": quantity,
            }
            for equipment, quantity in context["equipment_assignments"]
        ],
        "impact_facts": impact_facts,
    }

def record_crowding_observation(
    db: Session,
    event_id: int,
    room_id: int,
    observed_occupancy: int,
    confidence: float,
) -> dict:
    if observed_occupancy < 0:
        raise ValueError(
            "observed_occupancy cannot be negative"
        )

    if not 0 <= confidence <= 1:
        raise ValueError(
            "confidence must be between 0 and 1"
        )

    event = get_event(
        db,
        event_id,
    )

    if event is None:
        raise ValueError(
            "Event not found"
        )

    room = get_room(
        db,
        room_id,
    )

    if room is None:
        raise ValueError(
            "Room not found"
        )

    occupancy_ratio = (
        observed_occupancy / room.capacity
    )

    crowding = (
        observed_occupancy > room.capacity
    )

    if not crowding:
        return {
            "event_id": event.id,
            "room_id": room.id,
            "room_capacity": room.capacity,
            "observed_occupancy": observed_occupancy,
            "occupancy_ratio": occupancy_ratio,
            "crowding": False,
            "incident": None,
            "incident_created": False,
        }

    existing_incident = find_open_crowding_incident(
        db,
        event.id,
        room.id,
    )

    if existing_incident is not None:
        existing_incident.extra_data = {
            **(existing_incident.extra_data or {}),
            "observed_occupancy": observed_occupancy,
            "room_capacity": room.capacity,
            "confidence": confidence,
        }

        db.commit()
        db.refresh(existing_incident)

        return {
            "event_id": event.id,
            "room_id": room.id,
            "room_capacity": room.capacity,
            "observed_occupancy": observed_occupancy,
            "occupancy_ratio": occupancy_ratio,
            "crowding": True,
            "incident": existing_incident,
            "incident_created": False,
        }

    incident = Incident(
        event_id=event.id,
        room_id=room.id,
        type="CROWDING",
        severity="HIGH",
        status="OPEN",
        source="COMPUTER_VISION",
        title=f"{room.name} exceeds expected occupancy",
        description=(
            "Computer vision detected more people "
            "than the room capacity."
        ),
        extra_data={
            "observed_occupancy": observed_occupancy,
            "room_capacity": room.capacity,
            "confidence": confidence,
        },
    )

    repository_create_incident(
        db,
        incident,
    )

    db.commit()
    db.refresh(incident)

    return {
        "event_id": event.id,
        "room_id": room.id,
        "room_capacity": room.capacity,
        "observed_occupancy": observed_occupancy,
        "occupancy_ratio": occupancy_ratio,
        "crowding": True,
        "incident": incident,
        "incident_created": True,
    }