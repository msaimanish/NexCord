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