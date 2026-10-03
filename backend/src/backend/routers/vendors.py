from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.dependencies import get_db
from backend.schemas.vendor import (
    VendorAvailabilityRead,
    VendorRead,
)
from backend.services.vendor_service import (
    check_vendor_availability,
    get_vendor,
    list_vendors,
)

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
)


@router.get(
    "",
    response_model=list[VendorRead],
)
def get_vendors(
    db: Session = Depends(get_db),
):
    return list_vendors(db)

@router.get(
    "/{vendor_id}/availability",
    response_model=VendorAvailabilityRead,
)
def get_vendor_availability(
    vendor_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
):
    try:
        result = check_vendor_availability(
            db,
            vendor_id,
            start_time,
            end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    return result

@router.get(
    "/{vendor_id}",
    response_model=VendorRead,
)
def get_vendor_by_id(
    vendor_id: int,
    db: Session = Depends(get_db),
):
    vendor = get_vendor(
        db,
        vendor_id,
    )

    if vendor is None:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    return vendor