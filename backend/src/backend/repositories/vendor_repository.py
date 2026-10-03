from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Event, EventVendor, Vendor


def list_vendors(db: Session) -> list[Vendor]:
    statement = select(Vendor).order_by(Vendor.name)
    return list(db.scalars(statement).all())


def get_vendor(
    db: Session,
    vendor_id: int,
) -> Vendor | None:
    statement = select(Vendor).where(
        Vendor.id == vendor_id
    )
    return db.scalar(statement)

def find_vendor_assignment_conflicts(
    db: Session,
    vendor_id: int,
    start_time: datetime,
    end_time: datetime,
) -> list[tuple[Event, str, str]]:
    statement = (
        select(
            Event,
            EventVendor.service_type,
            EventVendor.status,
        )
        .join(
            EventVendor,
            EventVendor.event_id == Event.id,
        )
        .where(
            EventVendor.vendor_id == vendor_id,
            EventVendor.status == "ASSIGNED",
            Event.start_time < end_time,
            Event.end_time > start_time,
        )
        .order_by(Event.start_time)
    )

    return list(db.execute(statement).all())