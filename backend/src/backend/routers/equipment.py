from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.schemas.equipment import (
    EquipmentAvailabilityRead,
    EquipmentRead,
)
from backend.services.equipment_service import (
    check_equipment_availability,
    get_equipment,
    list_equipment,
)


router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
)

@router.get(
    "/{equipment_id}/availability",
    response_model=EquipmentAvailabilityRead,
)
def get_equipment_availability(
    equipment_id: int,
    requested_quantity: int,
    db: Session = Depends(get_db),
):
    try:
        result = check_equipment_availability(
            db,
            equipment_id,
            requested_quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if result["reason"] == "Equipment not found":
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    return result


@router.get(
    "",
    response_model=list[EquipmentRead],
)
def get_equipment_list(
    db: Session = Depends(get_db),
):
    return list_equipment(db)


@router.get(
    "/{equipment_id}",
    response_model=EquipmentRead,
)
def get_equipment_by_id(
    equipment_id: int,
    db: Session = Depends(get_db),
):
    equipment = get_equipment(
        db,
        equipment_id,
    )

    if equipment is None:
        raise HTTPException(
            status_code=404,
            detail="Equipment not found",
        )

    return equipment