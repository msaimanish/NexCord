from pydantic import BaseModel, ConfigDict
from datetime import datetime

class VendorRead(BaseModel):
    id: int
    name: str
    vendor_type: str
    contact_name: str
    phone: str | None
    email: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)

class VendorAvailabilityRead(BaseModel):
    vendor_id: int
    requested_start: datetime
    requested_end: datetime
    available: bool
    reason: str
    conflicts: list[dict]