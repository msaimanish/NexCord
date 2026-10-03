from sqlalchemy.orm import Session

from backend.models import Equipment
from backend.repositories.equipment_repository import (
    get_equipment as repository_get_equipment,
    list_equipment as repository_list_equipment,
)


def list_equipment(db: Session) -> list[Equipment]:
    return repository_list_equipment(db)


def get_equipment(
    db: Session,
    equipment_id: int,
) -> Equipment | None:
    return repository_get_equipment(
        db,
        equipment_id,
    )

def check_equipment_availability(
    db: Session,
    equipment_id: int,
    requested_quantity: int,
) -> dict:
    if requested_quantity <= 0:
        raise ValueError(
            "requested_quantity must be greater than 0"
        )

    equipment = get_equipment(db, equipment_id)

    if equipment is None:
        return {
            "equipment_id": equipment_id,
            "requested_quantity": requested_quantity,
            "available_quantity": 0,
            "available": False,
            "reason": "Equipment not found",
        }

    if equipment.status != "AVAILABLE":
        return {
            "equipment_id": equipment.id,
            "requested_quantity": requested_quantity,
            "available_quantity": equipment.available_quantity,
            "available": False,
            "reason": f"Equipment status is {equipment.status}",
        }

    if equipment.available_quantity < requested_quantity:
        return {
            "equipment_id": equipment.id,
            "requested_quantity": requested_quantity,
            "available_quantity": equipment.available_quantity,
            "available": False,
            "reason": (
                f"Only {equipment.available_quantity} "
                f"units are currently available"
            ),
        }

    return {
        "equipment_id": equipment.id,
        "requested_quantity": requested_quantity,
        "available_quantity": equipment.available_quantity,
        "available": True,
        "reason": "Sufficient equipment is available",
    }