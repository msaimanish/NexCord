from sqlalchemy.orm import Session
from datetime import datetime
from backend.models import Vendor
from backend.repositories.vendor_repository import (
    find_vendor_assignment_conflicts as repository_find_vendor_assignment_conflicts,
    get_vendor as repository_get_vendor,
    list_vendors as repository_list_vendors,
)


def list_vendors(db: Session) -> list[Vendor]:
    return repository_list_vendors(db)


def get_vendor(
    db: Session,
    vendor_id: int,
) -> Vendor | None:
    return repository_get_vendor(
        db,
        vendor_id,
    )

def check_vendor_availability(
    db: Session,
    vendor_id: int,
    start_time: datetime,
    end_time: datetime,
) -> dict | None:
    if start_time >= end_time:
        raise ValueError(
            "start_time must be earlier than end_time"
        )

    vendor = get_vendor(db, vendor_id)

    if vendor is None:
        return None

    if vendor.status != "ACTIVE":
        return {
            "vendor_id": vendor.id,
            "requested_start": start_time,
            "requested_end": end_time,
            "available": False,
            "reason": f"Vendor status is {vendor.status}",
            "conflicts": [],
        }

    conflicts = repository_find_vendor_assignment_conflicts(
        db,
        vendor_id,
        start_time,
        end_time,
    )

    conflict_data = [
        {
            "event_id": event.id,
            "event_name": event.name,
            "service_type": service_type,
            "assignment_status": assignment_status,
            "start_time": event.start_time,
            "end_time": event.end_time,
        }
        for event, service_type, assignment_status in conflicts
    ]

    if conflicts:
        return {
            "vendor_id": vendor.id,
            "requested_start": start_time,
            "requested_end": end_time,
            "available": False,
            "reason": "Vendor has an overlapping event assignment",
            "conflicts": conflict_data,
        }

    return {
        "vendor_id": vendor.id,
        "requested_start": start_time,
        "requested_end": end_time,
        "available": True,
        "reason": "Vendor is active and has no overlapping assignment",
        "conflicts": [],
    }