from typing import Any, Literal

from pydantic import BaseModel


class ExpectedOutcome(BaseModel):
    task_completed: bool
    verification_success: bool
    recovery_required: bool = False
    recovery_success: bool = False


class EvaluationScenario(BaseModel):
    scenario_id: str
    name: str

    event_id: int

    initial_state: dict[str, Any]

    user_request: str

    incident: dict[str, Any]

    expected_impact: dict[str, Any]

    allowed_actions: list[str]
    unsafe_actions: list[str]
    expected_action_types: list[str] = []

    desired_final_state: dict[str, Any]

    expected_outcome: ExpectedOutcome

    approval_decision: Literal["approve", "reject"] = "approve"
    
    plan_quality_requirements: dict[str, Any] = {}
    
    reset_fixture: dict[str, Any] = {}