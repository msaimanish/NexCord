from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.execution import ExecutionRead
from backend.dependencies import get_db
from backend.schemas.plan import (
    PlanApprovalRequest,
    PlanRead,
)
from backend.services.plan_service import (
    approve_plan,
    commit_plan,
    generate_candidate_plans,
    recover_execution,
    simulate_plan,
    verify_execution,
)
from backend.repositories.plan_repository import (
    get_plan,
    list_plans_for_incident,
)
from backend.repositories.execution_repository import (
    get_execution,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Plans"],
)

@router.post(
    "/{incident_id}/executions/{execution_id}/recover",
    response_model=ExecutionRead,
)
def recover_existing_execution(
    incident_id: int,
    execution_id: int,
    db: Session = Depends(get_db),
):
    execution = get_execution(
        db,
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    plan = get_plan(
        db,
        execution.plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found",
        )

    if plan.incident_id != incident_id:
        raise HTTPException(
            status_code=400,
            detail="Execution does not belong to this incident",
        )

    recovery_execution, error = recover_execution(
        db,
        execution_id,
    )

    if recovery_execution is None:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return recovery_execution

@router.post(
    "/{incident_id}/executions/{execution_id}/verify",
    response_model=ExecutionRead,
)
def verify_existing_execution(
    incident_id: int,
    execution_id: int,
    db: Session = Depends(get_db),
):
    execution = get_execution(
        db,
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    plan = get_plan(
        db,
        execution.plan_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found",
        )

    if plan.incident_id != incident_id:
        raise HTTPException(
            status_code=400,
            detail="Execution does not belong to this incident",
        )

    execution, error = verify_execution(
        db,
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return execution

@router.post(
    "/{incident_id}/plans/{plan_id}/commit",
    response_model=ExecutionRead,
)
def commit_existing_plan(
    incident_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
):
    plan = get_plan(db, plan_id)

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found",
        )

    if plan.incident_id != incident_id:
        raise HTTPException(
            status_code=400,
            detail="Plan does not belong to this incident",
        )

    execution, error = commit_plan(
        db,
        plan_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return execution

@router.post(
    "/{incident_id}/plans/{plan_id}/approve",
    response_model=PlanRead,
)
def approve_existing_plan(
    incident_id: int,
    plan_id: int,
    request: PlanApprovalRequest,
    db: Session = Depends(get_db),
):
    plan, error = approve_plan(
        db,
        plan_id,
        request.approved_by_person_id,
    )

    if plan is None:
        if error == "Plan not found":
            raise HTTPException(
                status_code=404,
                detail=error,
            )

        raise HTTPException(
            status_code=400,
            detail=error,
        )

    if plan.incident_id != incident_id:
        raise HTTPException(
            status_code=400,
            detail="Plan does not belong to this incident",
        )

    return plan

@router.post(
    "/{incident_id}/plans/{plan_id}/simulate",
    response_model=PlanRead,
)
def simulate_existing_plan(
    incident_id: int,
    plan_id: int,
    db: Session = Depends(get_db),
):
    plan = simulate_plan(db, plan_id)

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found",
        )

    if plan.incident_id != incident_id:
        raise HTTPException(
            status_code=400,
            detail="Plan does not belong to this incident",
        )

    return plan

@router.post(
    "/{incident_id}/plans/generate",
    response_model=list[PlanRead],
)
def generate_plans(
    incident_id: int,
    db: Session = Depends(get_db),
):
    plans = generate_candidate_plans(
        db,
        incident_id,
    )

    if plans is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return plans


@router.get(
    "/{incident_id}/plans",
    response_model=list[PlanRead],
)
def get_plans(
    incident_id: int,
    db: Session = Depends(get_db),
):
    plans = list_plans_for_incident(
        db,
        incident_id,
    )

    return plans