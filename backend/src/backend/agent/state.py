from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_request: str
    event_id: int
    event_state: dict[str, Any]
    incidents: list[dict[str, Any]]
    detected_problems: list[dict[str, Any]]
    predictions: dict[str, Any]
    retrieved_context: list[dict[str, Any]]
    candidate_plans: list[dict[str, Any]]
    simulated_plans: list[dict[str, Any]]
    simulated_plans: list[dict[str, Any]]
    selected_plan: dict[str, Any] | None
    approved_by_person_id: int
    approval_status: str
    execution_result: dict[str, Any] | None
    verification_result: dict[str, Any] | None
    recovery_result: dict[str, Any] | None
    incident_impacts: list[dict[str, Any]]
    response: str