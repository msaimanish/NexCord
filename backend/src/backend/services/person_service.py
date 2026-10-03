from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Person
from backend.repositories.person_repository import (
    find_person_assignment_conflicts as repository_find_person_assignment_conflicts,
    get_person as repository_get_person,
    list_people as repository_list_people,
)

def list_people(db: Session) -> list[Person]:
    return repository_list_people(db)


def get_person(
    db: Session,
    person_id: int,
) -> Person | None:
    return repository_get_person(
        db,
        person_id,
    )

def check_person_availability(
    db: Session,
    person_id: int,
    start_time: datetime,
    end_time: datetime,
) -> dict | None:
    if start_time >= end_time:
        raise ValueError(
            "start_time must be earlier than end_time"
        )

    person = get_person(db, person_id)

    if person is None:
        return None

    conflicts = repository_find_person_assignment_conflicts(
        db,
        person_id,
        start_time,
        end_time,
    )

    conflict_data = [
        {
            "event_id": event.id,
            "event_name": event.name,
            "assignment_role": assignment_role,
            "start_time": event.start_time,
            "end_time": event.end_time,
        }
        for event, assignment_role in conflicts
    ]

    if conflicts:
        return {
            "person_id": person.id,
            "requested_start": start_time,
            "requested_end": end_time,
            "available": False,
            "reason": "Person has overlapping event assignments",
            "conflicts": conflict_data,
        }

    return {
        "person_id": person.id,
        "requested_start": start_time,
        "requested_end": end_time,
        "available": True,
        "reason": "No overlapping event assignments",
        "conflicts": [],
    }