from pydantic import BaseModel, ConfigDict


class RoomRead(BaseModel):
    id: int
    venue_id: int
    name: str
    capacity: int
    floor: int | None
    status: str

    model_config = ConfigDict(from_attributes=True)