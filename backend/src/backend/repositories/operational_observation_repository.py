from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import OperationalObservation


def create_observation(
    db: Session,
    observation: OperationalObservation,
) -> OperationalObservation:

    db.add(observation)
    db.flush()

    return observation


def list_observations_for_event(
    db: Session,
    event_id: int,
) -> list[OperationalObservation]:

    statement = (
        select(OperationalObservation)
        .where(
            OperationalObservation.event_id == event_id
        )
        .order_by(
            OperationalObservation.observed_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_latest_observation(
    db: Session,
    event_id: int,
) -> OperationalObservation | None:

    statement = (
        select(OperationalObservation)
        .where(
            OperationalObservation.event_id == event_id
        )
        .order_by(
            OperationalObservation.observed_at.desc()
        )
        .limit(1)
    )

    return db.scalar(statement)