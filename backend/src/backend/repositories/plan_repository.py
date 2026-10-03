from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models import Plan


def list_plans_for_incident(
    db: Session,
    incident_id: int,
) -> list[Plan]:
    statement = (
        select(Plan)
        .options(selectinload(Plan.actions))
        .where(Plan.incident_id == incident_id)
        .order_by(Plan.id)
    )

    return list(db.scalars(statement).unique().all())


def create_plan(
    db: Session,
    plan: Plan,
) -> Plan:
    db.add(plan)
    db.flush()

    return plan

def get_plan(db: Session, plan_id: int):
    statement = (
        select(Plan)
        .options(selectinload(Plan.actions))
        .where(Plan.id == plan_id)
    )

    return db.scalars(statement).unique().one_or_none()