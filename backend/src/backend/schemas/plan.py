from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pydantic import BaseModel


class PlanApprovalRequest(BaseModel):
    approved_by_person_id: int

class PlanActionRead(BaseModel):
    id: int
    sequence: int
    action_type: str
    description: str
    parameters: dict | None
    expected_result: dict | None
    compensation: dict | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class PlanRead(BaseModel):
    id: int
    incident_id: int
    summary: str
    rationale: str | None
    status: str
    risk_level: str
    estimated_cost: float | None
    estimated_delay_minutes: int | None
    simulation_result: dict | None
    expected_state: dict | None
    approved_by_person_id: int | None
    approved_at: datetime | None

    actions: list[PlanActionRead]

    model_config = ConfigDict(from_attributes=True)