from pydantic import BaseModel, ConfigDict


class EquipmentRead(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    available_quantity: int
    status: str

    model_config = ConfigDict(from_attributes=True)

class EquipmentAvailabilityRead(BaseModel):
    equipment_id: int
    requested_quantity: int
    available_quantity: int
    available: bool
    reason: str