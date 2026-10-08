from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from langgraph.types import Command

from backend.agent.graph import build_graph


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


graph = build_graph()


class AgentRunRequest(BaseModel):
    user_request: str
    event_id: int
    approved_by_person_id: int = 1
    thread_id: str


class AgentResumeRequest(BaseModel):
    thread_id: str
    approved: bool


def format_result(
    result: dict[str, Any],
    thread_id: str,
) -> dict[str, Any]:

    interrupts = result.get(
        "__interrupt__",
        [],
    )

    approval_request = None

    if interrupts:
        approval_request = interrupts[0].value

    return {
        "thread_id": thread_id,

        "status": (
            "AWAITING_APPROVAL"
            if interrupts
            else result.get(
                "approval_status",
                "COMPLETED",
            )
        ),

        "approval_request": approval_request,

        "response": result.get(
            "response",
        ),

        "selected_plan": result.get(
            "selected_plan",
        ),

        "candidate_plans": result.get(
            "candidate_plans",
            [],
        ),

        "simulated_plans": result.get(
            "simulated_plans",
            [],
        ),

        "detected_problems": result.get(
            "detected_problems",
            [],
        ),

        "predictions": result.get(
            "predictions",
            {},
        ),

        "execution_result": result.get(
            "execution_result",
        ),

        "verification_result": result.get(
            "verification_result",
        ),

        "recovery_result": result.get(
            "recovery_result",
        ),

        "approval_status": result.get(
            "approval_status",
        ),
    }


@router.post("/run")
def run_agent(
    request: AgentRunRequest,
):
    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = graph.invoke(
        {
            "user_request": request.user_request,
            "event_id": request.event_id,
            "approved_by_person_id": (
                request.approved_by_person_id
            ),
        },
        config=config,
    )

    return format_result(
        result,
        request.thread_id,
    )


@router.post("/resume")
def resume_agent(
    request: AgentResumeRequest,
):
    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = graph.invoke(
        Command(
            resume=request.approved,
        ),
        config=config,
    )

    return format_result(
        result,
        request.thread_id,
    )
