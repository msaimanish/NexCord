from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Event, EventPerson, Person


def list_people(db: Session) -> list[Person]:
    statement = select(Person).order_by(Person.name)
    return list(db.scalars(statement).all())


def get_person(
    db: Session,
    person_id: int,
) -> Person | None:
    statement = select(Person).where(
        Person.id == person_id
    )
    return db.scalar(statement)

def find_person_assignment_conflicts(
    db: Session,
    person_id: int,
    start_time: datetime,
    end_time: datetime,
) -> list[tuple[Event, str]]:
    statement = (
        select(Event, EventPerson.assignment_role)
        .join(
            EventPerson,
            EventPerson.event_id == Event.id,
        )
        .where(
            EventPerson.person_id == person_id,
            Event.start_time < end_time,
            Event.end_time > start_time,
        )
        .order_by(Event.start_time)
    )

    return list(db.execute(statement).all())