from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Equipment


def list_equipment(db: Session) -> list[Equipment]:
    statement = select(Equipment).order_by(Equipment.name)
    return list(db.scalars(statement).all())


def get_equipment(
    db: Session,
    equipment_id: int,
) -> Equipment | None:
    statement = select(Equipment).where(
        Equipment.id == equipment_id
    )
    return db.scalar(statement)