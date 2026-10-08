import json
import os
import httpx

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from backend.agent.llm_client import (
    LLMClient,
)

from backend.agent.state import AgentState
from backend.database import SessionLocal
from backend.services.knowledge_service import query_knowledge
from backend.services.incident_service import (
    analyze_incident_impact,
)
from backend.services.plan_service import (
    approve_plan,
    generate_candidate_plans,
    simulate_plan,
)

from backend.agent.mcp_client import NexCordMCPClient
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver



BASE_URL = "http://127.0.0.1:8000"
ML_URL = "http://127.0.0.1:8100"

def observe_node(
    state: AgentState,
) -> dict:
    event_id = state["event_id"]

    response = httpx.get(
        f"{BASE_URL}/api/v1/events/{event_id}/state",
        timeout=10.0,
    )

    response.raise_for_status()

    event_state = response.json()

    return {
        "event_state": event_state,
        "incidents": event_state.get(
            "incidents",
            [],
        ),
    }


def reason_node(
    state: AgentState,
) -> dict:

    if os.getenv("NEXCORD_EVAL_MODE") == "1":
        return {
            "response": "Evaluation mode: reasoning response generation skipped."
        }

    llm = LLMClient()

    event_state = state["event_state"]
    selected_plan = state.get("selected_plan")

    prompt = f"""
You are NexCord, an event operations intelligence assistant.

Your response must primarily address the user's request and the
response plan NexCord has already selected.

User request:
{state["user_request"]}

Selected response plan:
{json.dumps(selected_plan, indent=2)}

Operational state:
{json.dumps(event_state, indent=2)}

Detected problems:
{json.dumps(state.get("detected_problems", []), indent=2)}

ML predictions:
{json.dumps(state.get("predictions", {}), indent=2)}

Retrieved operational knowledge:
{json.dumps(state.get("retrieved_context", []), indent=2)}

Incident impact analysis:
{json.dumps(state.get("incident_impacts", []), indent=2)}

Candidate response plans:
{json.dumps(state.get("candidate_plans", []), indent=2)}

Simulated response plans:
{json.dumps(state.get("simulated_plans", []), indent=2)}

Follow these rules carefully:

1. The user's request is the primary focus of the response.

2. Start by addressing the incident or problem the user asked about.

3. Treat the Selected response plan as NexCord's current best
   proposed solution because it has already passed simulation.

4. Explain the selected plan clearly:
   - what action will be taken
   - why it is appropriate
   - expected impact
   - estimated delay
   - risk level

5. Do NOT replace the selected plan with another plan.

6. Other incidents may be mentioned as secondary context when they
   materially affect the user's request, but they must not dominate
   the response.

7. Do not invent facts, capabilities, vendor commitments, staff
   availability, room infrastructure, or operational results that
   are not present in the supplied data.

8. Clearly distinguish between:
   - confirmed current state
   - simulated/expected state
   - proposed action

9. No irreversible action has been executed yet.
   Human approval is required before execution.

10. This is an analysis/proposal response only. Do not claim that
    the selected plan has already been executed or verified.

Structure the response like this:

### Situation
Briefly describe the incident the user asked about.

### Recommended Plan
Describe the selected plan.

### Expected Impact
State the expected state change, cost, delay, and risk.

### Other Relevant Issues
Mention only other incidents that materially affect this request.

### Approval
State that human approval is required before execution.

Keep the response concise and operationally useful.
"""

    response = llm.generate(
        prompt
    )

    return {
        "response": response,
    }

def predict_node(state):
    event_id = state["event_id"]

    response = httpx.post(
        f"{ML_URL}/predict",
        json={"event_id": event_id},
        timeout=30.0,
    )

    response.raise_for_status()

    result = response.json()

    return {
        "predictions": result["prediction"]
    }

def retrieve_node(state):
    detected_problems = state.get(
        "detected_problems",
        [],
    )

    problem_types = [
        problem["type"]
        for problem in detected_problems
    ]

    query = (
        "Operational response guidance for "
        "the following event problems: "
        f"{', '.join(problem_types)}. "
        f"User request: {state['user_request']}. "
        "Focus on safety, venue capacity, "
        "equipment failures, staffing, "
        "and incident response procedures."
    )

    db = SessionLocal()

    try:
        result = query_knowledge(
            db,
            query,
            top_k=5,
        )
    finally:
        db.close()

    return {
        "retrieved_context": result["results"]
    }

def analyze_impact_node(state):
    detected_problems = state.get(
        "detected_problems",
        [],
    )

    db = SessionLocal()

    incident_impacts = []

    try:
        for problem in detected_problems:
            incident_id = problem["incident_id"]

            impact = analyze_incident_impact(
                db,
                incident_id,
            )

            if impact is None:
                continue

            incident = impact["incident"]

            affected_room = impact["affected_room"]
            affected_vendor = impact["affected_vendor"]
            affected_person = impact["affected_person"]
            affected_equipment = impact["affected_equipment"]

            incident_impacts.append(
                {
                    "incident_id": incident.id,
                    "type": incident.type,
                    "severity": incident.severity,
                    "impact_facts": impact["impact_facts"],
                    "affected_room": (
                        {
                            "id": affected_room.id,
                            "name": affected_room.name,
                            "capacity": affected_room.capacity,
                        }
                        if affected_room is not None
                        else None
                    ),
                    "affected_vendor": (
                        {
                            "id": affected_vendor.id,
                            "name": affected_vendor.name,
                        }
                        if affected_vendor is not None
                        else None
                    ),
                    "affected_person": (
                        {
                            "id": affected_person.id,
                            "name": affected_person.name,
                        }
                        if affected_person is not None
                        else None
                    ),
                    "affected_equipment": (
                        {
                            "id": affected_equipment.id,
                            "name": affected_equipment.name,
                        }
                        if affected_equipment is not None
                        else None
                    ),
                    "conflicting_reservation_count": len(
                        impact["conflicting_reservations"]
                    ),
                    "active_reservation_count": len(
                        impact["active_reservations"]
                    ),
                }
            )

    finally:
        db.close()

    return {
        "incident_impacts": incident_impacts
    }

def generate_plans_node(state):
    detected_problems = state.get(
        "detected_problems",
        [],
    )

    db = SessionLocal()

    candidate_plans = []

    try:
        for problem in detected_problems:
            if problem["type"] not in (
                "ROOM_DOUBLE_BOOKED",
                "CROWDING",
                "EQUIPMENT_FAILURE",
            ):
                continue

            incident_id = problem["incident_id"]

            plans = generate_candidate_plans(
                db,
                incident_id,
            )

            if not plans:
                continue

            for plan in plans:
                # Do not treat already executed or verified
                # plans as new candidate plans.
                if plan.status != "PROPOSED":
                    continue

                candidate_plans.append(
                    {
                        "plan_id": plan.id,
                        "incident_id": plan.incident_id,
                        "summary": plan.summary,
                        "rationale": plan.rationale,
                        "status": plan.status,
                        "risk_level": plan.risk_level,
                        "estimated_cost": plan.estimated_cost,
                        "estimated_delay_minutes": (
                            plan.estimated_delay_minutes
                        ),
                        "expected_state": plan.expected_state,
                        "actions": [
                            {
                                "sequence": action.sequence,
                                "action_type": action.action_type,
                                "description": action.description,
                                "parameters": action.parameters,
                                "expected_result": (
                                    action.expected_result
                                ),
                            }
                            for action in plan.actions
                        ],
                    }
                )

    finally:
        db.close()

    return {
        "candidate_plans": candidate_plans
    }

def simulate_node(state):
    candidate_plans = state.get(
        "candidate_plans",
        []
    )

    db = SessionLocal()

    simulated_plans = []

    try:
        for candidate in candidate_plans:
            plan_id = candidate["plan_id"]

            plan = simulate_plan(
                db,
                plan_id,
            )

            if plan is None:
                continue

            simulation_result = (
                plan.simulation_result or {}
            )

            simulated_plans.append(
                {
                    **candidate,
                    "simulation_result": simulation_result,
                    "simulation_success": (
                        simulation_result.get(
                            "success",
                            False,
                        )
                    ),
                }
            )

    finally:
        db.close()

    return {
        "simulated_plans": simulated_plans
    }

def select_plan_node(state: AgentState):
    simulated_plans = state.get("simulated_plans", [])

    successful_plans = [
        plan
        for plan in simulated_plans
        if (
            plan.get("simulation_result")
            and plan["simulation_result"].get("success") is True
        )
    ]

    if not successful_plans:
        return {
            "selected_plan": None,
            "approval_status": "NO_VALID_PLAN",
        }

    user_request = (state.get("user_request") or "").lower()

    requested_type = None

    if any(
        word in user_request
        for word in (
            "projector",
            "equipment",
            "device",
            "display",
            "screen",
        )
    ):
        requested_type = "EQUIPMENT_FAILURE"

    elif any(
        word in user_request
        for word in (
            "crowd",
            "overcrowd",
            "capacity",
        )
    ):
        requested_type = "CROWDING"

    elif any(
        word in user_request
        for word in (
            "double book",
            "double-book",
            "reservation conflict",
        )
    ):
        requested_type = "ROOM_DOUBLE_BOOKED"

    elif any(
        word in user_request
        for word in (
            "judge",
            "staff",
            "person unavailable",
        )
    ):
        requested_type = "PERSON_UNAVAILABLE"

    elif any(
        word in user_request
        for word in (
            "caterer",
            "catering",
            "vendor",
        )
    ):
        requested_type = "VENDOR_CANCELLED"

    detected_problems = state.get("detected_problems", [])

    problem_type_by_incident = {
        problem["incident_id"]: problem["type"]
        for problem in detected_problems
        if problem.get("incident_id") is not None
    }

    def sort_key(plan):
        incident_type = problem_type_by_incident.get(
            plan.get("incident_id")
        )

        intent_match = (
            0
            if requested_type is not None
            and incident_type == requested_type
            else 1
        )

        risk_rank = {
            "LOW": 0,
            "MEDIUM": 1,
            "HIGH": 2,
        }.get(plan.get("risk_level", "HIGH"), 3)

        delay = plan.get("estimated_delay_minutes", 999999)
        cost = plan.get("estimated_cost", 999999)

        return (
            intent_match,
            risk_rank,
            delay,
            cost,
        )

    selected_plan = sorted(
        successful_plans,
        key=sort_key,
    )[0]

    return {
        "selected_plan": selected_plan,
    }


def approval_node(state: AgentState) -> dict:
    selected_plan = state.get("selected_plan")

    if selected_plan is None:
        return {
            "approval_status": "NO_VALID_PLAN",
        }

    decision = interrupt(
        {
            "type": "approval_required",
            "message": "NexCord has selected a plan. Approve execution?",
            "plan": selected_plan,
        }
    )

    if decision is True:
        db = SessionLocal()

        try:
            plan_id = selected_plan["plan_id"]

            plan, error = approve_plan(
                db,
                plan_id,
                state["approved_by_person_id"],
            )
        finally:
            db.close()

        if plan is None:
            return {
                "approval_status": "APPROVAL_FAILED",
            }

        return {
            "approval_status": "APPROVED",
        }

    return {
        "approval_status": "REJECTED",
    }

def execute_node(state: AgentState) -> dict:
    if state.get("approval_status") != "APPROVED":
        return {
            "execution_result": None,
        }

    selected_plan = state.get("selected_plan")

    if selected_plan is None:
        return {
            "execution_result": None,
        }

    client = NexCordMCPClient()

    result = client.call(
        "commit_plan",
        {
            "plan_id": selected_plan["plan_id"],
        },
    )

    if getattr(result, "is_error", False):
        return {
            "execution_result": {
                "success": False,
                "error": "MCP commit_plan returned an error.",
            }
        }

    if not result.content:
        return {
            "execution_result": {
                "success": False,
                "error": "MCP commit_plan returned no content.",
            }
        }

    payload = json.loads(
        result.content[0].text
    )

    return {
        "execution_result": payload,
    }

def verify_node(state: AgentState) -> dict:
    execution_result = state.get("execution_result")

    if not execution_result:
        return {
            "verification_result": None,
        }

    execution = execution_result.get("execution")

    if not execution:
        return {
            "verification_result": {
                "success": False,
                "error": execution_result.get(
                    "error",
                    "No execution was created.",
                ),
            },
        }

    execution_id = execution["id"]

    client = NexCordMCPClient()

    result = client.call(
        "verify_execution",
        {
            "execution_id": execution_id,
        },
    )

    if getattr(result, "is_error", False):
        return {
            "verification_result": {
                "success": False,
                "execution_id": execution_id,
                "error": "MCP verify_execution returned an error.",
            }
        }

    if not result.content:
        return {
            "verification_result": {
                "success": False,
                "execution_id": execution_id,
                "error": "MCP verify_execution returned no content.",
            }
        }

    payload = json.loads(
        result.content[0].text
    )

    return {
        "verification_result": payload,
    }

def recover_node(state: AgentState) -> dict:
    execution_result = state.get("execution_result")

    if not execution_result:
        return {
            "recovery_result": None,
        }

    execution = execution_result.get("execution")

    if not execution:
        return {
            "recovery_result": {
                "success": False,
                "error": "No execution available for recovery.",
            }
        }

    execution_id = execution["id"]

    client = NexCordMCPClient()

    result = client.call(
        "recover_execution",
        {
            "execution_id": execution_id,
        },
    )

    if getattr(result, "is_error", False):
        return {
            "recovery_result": {
                "success": False,
                "execution_id": execution_id,
                "error": "MCP recover_execution returned an error.",
            }
        }

    if not result.content:
        return {
            "recovery_result": {
                "success": False,
                "execution_id": execution_id,
                "error": "MCP recover_execution returned no content.",
            }
        }

    payload = json.loads(
        result.content[0].text
    )

    return {
        "recovery_result": payload,
    }

def route_after_approval(state: AgentState) -> str:
    if state.get("approval_status") == "APPROVED":
        return "execute"

    return "end"

def route_after_execute(state: AgentState) -> str:
    execution_result = state.get("execution_result")

    if not execution_result:
        return "end"

    if execution_result.get("success") is True:
        return "verify"

    execution = execution_result.get("execution")

    if execution:
        return "recover"

    return "end"

def route_after_verify(state: AgentState) -> str:
    verification_result = state.get("verification_result")

    if verification_result and verification_result.get(
        "success"
    ) is True:
        return "end"

    return "recover"

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("observe", observe_node)
    builder.add_node("detect", detect_node)
    builder.add_node("predict", predict_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node(
        "analyze_impact",
        analyze_impact_node,
    )
    builder.add_node(
        "generate_plans",
        generate_plans_node,
    )
    builder.add_node(
        "simulate",
        simulate_node,
    )
    builder.add_node(
        "select_plan",
        select_plan_node,
    )
    builder.add_node("reason", reason_node)
    builder.add_node(
        "execute",
        execute_node,
    )

    builder.add_node(
        "verify",
        verify_node,
    )

    builder.add_node(
        "recover",
        recover_node,
    )

    builder.add_node("approval", approval_node)

    builder.add_edge(
        START,
        "observe",
    )
    builder.add_edge(
        "observe",
        "detect",
    )
    builder.add_edge(
        "detect",
        "predict",
    )
    builder.add_edge(
        "predict",
        "retrieve",
    )
    builder.add_edge(
        "retrieve",
        "analyze_impact",
    )
    builder.add_edge(
        "analyze_impact",
        "generate_plans",
    )
    builder.add_edge(
        "generate_plans",
        "simulate",
    )
    builder.add_edge(
        "simulate",
        "select_plan",
    )

    builder.add_edge(
        "select_plan",
        "reason",
    )

    builder.add_edge(
        "reason",
        "approval",
    )

    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "execute": "execute",
            "end": END,
        },
    )

    builder.add_conditional_edges(
        "execute",
        route_after_execute,
        {
            "verify": "verify",
            "recover": "recover",
            "end": END,
        },
    )

    builder.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "recover": "recover",
            "end": END,
        },
    )

    builder.add_edge(
        "recover",
        END,
    )

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

def detect_node(state):
    incidents = state.get("incidents", [])

    detected_problems = []

    for incident in incidents:
        detected_problems.append(
            {
                "incident_id": incident["id"],
                "type": incident["type"],
                "severity": incident["severity"],
                "source": incident["source"],
                "summary": incident.get("description"),
            }
        )

    detected_problems.sort(
        key=lambda problem: {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
        }.get(problem["severity"].lower(), 99)
    )

    return {"detected_problems": detected_problems}