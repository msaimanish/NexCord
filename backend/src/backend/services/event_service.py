from sqlalchemy.orm import Session

from backend.models import Event
from backend.repositories.event_repository import (
    get_event as repository_get_event,
    list_events as repository_list_events,
    get_event_operational_state as repository_get_event_operational_state,
)


def list_events(db: Session) -> list[Event]:
    return repository_list_events(db)


def get_event(db: Session, event_id: int) -> Event | None:
    return repository_get_event(db, event_id)

def get_event_operational_state(
    db: Session,
    event_id: int,
) -> dict | None:
    context = repository_get_event_operational_state(
        db,
        event_id,
    )

    if context is None:
        return None

    incidents = context["incidents"]
    conflicts = context["conflicting_reservations"]

    open_incidents = [
        incident
        for incident in incidents
        if incident.status == "OPEN"
    ]

    state_facts = []

    state_facts.append(
        f"Event has {len(context['reservations'])} "
        f"active room reservation(s)."
    )

    state_facts.append(
        f"Event has {len(context['people'])} "
        f"assigned person(s)."
    )

    state_facts.append(
        f"Event has {len(context['vendors'])} "
        f"assigned vendor(s)."
    )

    state_facts.append(
        f"Event has {len(context['equipment'])} "
        f"equipment assignment(s)."
    )

    if conflicts:
        state_facts.append(
            f"Event has {len(conflicts)} "
            f"conflicting reservation(s)."
        )

    if open_incidents:
        state_facts.append(
            f"Event has {len(open_incidents)} open incident(s)."
        )

        for incident in open_incidents:
            state_facts.append(
                f"Open incident: {incident.title} "
                f"[{incident.severity}]."
            )
    else:
        state_facts.append(
            "Event has no open incidents."
        )

    return {
        "event": context["event"],
        "reservations": context["reservations"],
        "conflicting_reservations": context[
            "conflicting_reservations"
        ],
        "incidents": incidents,
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
            for equipment, quantity in context["equipment"]
        ],
        "open_incident_count": len(open_incidents),
        "state_facts": state_facts,
    }