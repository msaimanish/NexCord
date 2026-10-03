from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExecutionRead(BaseModel):
    id: int
    plan_id: int
    execution_type: str
    status: str
    result: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)