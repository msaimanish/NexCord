from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Execution


def create_execution(
    db: Session,
    execution: Execution,
) -> Execution:
    db.add(execution)
    db.flush()
    return execution


def get_execution(
    db: Session,
    execution_id: int,
) -> Execution | None:
    statement = (
        select(Execution)
        .where(Execution.id == execution_id)
    )

    return db.scalars(statement).one_or_none()