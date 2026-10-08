from sqlalchemy.orm import Session

from sqlalchemy import select

from datetime import datetime, timezone

from backend.repositories.plan_repository import (

    create_plan,

    get_plan,

    list_plans_for_incident,

)

from backend.services.incident_service import (

    analyze_incident_impact,

)

from backend.services.room_service import (

    find_available_rooms,

)

from backend.models import (

    Execution,

    Plan,

    PlanAction,

    Reservation,

    Room,

    Event,

    Person,

    Equipment,

    EventEquipment,

)

from backend.repositories.execution_repository import (

    create_execution,

    get_execution,

)



def _get_required_capacity(

    impact: dict,

) -> int:

    room = impact["affected_room"]



    required_capacity = (

        room.capacity

        if room is not None

        else 1

    )



    for incident in impact["incidents"]:

        if incident.type == "CROWDING" and incident.extra_data:

            observed = incident.extra_data.get(

                "observed_occupancy"

            )



            if isinstance(observed, int):

                required_capacity = max(

                    required_capacity,

                    observed,

                )



    return required_capacity



def _times_overlap(

    start_a,

    end_a,

    start_b,

    end_b,

) -> bool:

    return start_a < end_b and end_a > start_b



def generate_candidate_plans(

    db: Session,

    incident_id: int,

) -> list[Plan] | None:

    impact = analyze_incident_impact(

        db,

        incident_id,

    )



    if impact is None:

        return None



    existing_plans = list_plans_for_incident(

        db,

        incident_id,

    )



    proposed_plans = [

        plan

        for plan in existing_plans

        if plan.status == "PROPOSED"

    ]



    if proposed_plans:

        return proposed_plans



    incident = impact["incident"]

    event = impact["event"]

    affected_room = impact["affected_room"]



    # ---------------------------------------------------------

    # EQUIPMENT FAILURE

    # ---------------------------------------------------------

    if incident.type == "EQUIPMENT_FAILURE":

        equipment = impact["affected_equipment"]



        if equipment is None:

            return []



        # The event must currently have this equipment assigned.

        assignment = db.scalar(

            select(EventEquipment).where(

                EventEquipment.event_id == event.id,

                EventEquipment.equipment_id == equipment.id,

            )

        )



        if assignment is None:

            return []



        # We need at least one available unit to act as a backup.

        if equipment.available_quantity < 1:

            return []



        if equipment.status.upper() != "AVAILABLE":

            return []



        original_assigned_quantity = assignment.quantity

        original_available_quantity = (

            equipment.available_quantity

        )



        expected_assigned_quantity = (

            original_assigned_quantity + 1

        )



        expected_available_quantity = (

            original_available_quantity - 1

        )



        plan = Plan(

            incident_id=incident.id,

            summary=(

                f"Allocate a backup {equipment.name} "

                f"to {event.name}"

            ),

            rationale=(

                f"{event.name} currently has "

                f"{original_assigned_quantity} assigned "

                f"{equipment.name}(s), while one unit has "

                f"been reported offline. "

                f"{original_available_quantity} additional "

                f"unit(s) are available, so one backup unit "

                f"can be allocated without creating an "

                f"inventory shortage."

            ),

            status="PROPOSED",

            risk_level="LOW",

            estimated_cost=0,

            estimated_delay_minutes=5,

            simulation_result=None,

            expected_state={

                "event_id": event.id,

                "equipment_id": equipment.id,

                "equipment_name": equipment.name,

                "original_assigned_quantity": (

                    original_assigned_quantity

                ),

                "expected_assigned_quantity": (

                    expected_assigned_quantity

                ),

                "original_available_quantity": (

                    original_available_quantity

                ),

                "expected_available_quantity": (

                    expected_available_quantity

                ),

            },

        )



        plan.actions = [

            PlanAction(

                sequence=1,

                action_type="ASSIGN_BACKUP_EQUIPMENT",

                description=(

                    f"Allocate one available {equipment.name} "

                    f"as backup equipment for {event.name}."

                ),

                parameters={

                    "event_id": event.id,

                    "equipment_id": equipment.id,

                    "quantity": 1,

                },

                expected_result={

                    "event_id": event.id,

                    "equipment_id": equipment.id,

                    "quantity": 1,

                    "status": "ASSIGNED",

                },

                compensation={

                    "action_type": "RELEASE_BACKUP_EQUIPMENT",

                    "event_id": event.id,

                    "equipment_id": equipment.id,

                    "quantity": 1,

                },

                status="PENDING",

            ),

        ]



        create_plan(

            db,

            plan,

        )



        db.commit()



        return [plan]



    # ---------------------------------------------------------

    # ROOM-BASED INCIDENTS

    # ---------------------------------------------------------

    if incident.type not in (

        "ROOM_DOUBLE_BOOKED",

        "CROWDING",

    ):

        return []



    if affected_room is None:

        return []



    required_capacity = _get_required_capacity(

        impact

    )



    candidate_rooms = find_available_rooms(

        db,

        event.start_time,

        event.end_time,

        required_capacity,

    )



    plans = []



    for room in candidate_rooms:

        plan = Plan(

            incident_id=incident.id,

            summary=(

                f"Move {event.name} "

                f"from {affected_room.name} "

                f"to {room.name}"

            ),

            rationale=(

                f"{room.name} has capacity {room.capacity}, "

                f"meets the required capacity of "

                f"{required_capacity}, and has no "

                f"conflicting active reservation "

                f"during the event."

            ),

            status="PROPOSED",

            risk_level="LOW",

            estimated_cost=0,

            estimated_delay_minutes=0,

            simulation_result=None,

            expected_state={

                "event_id": event.id,

                "target_room_id": room.id,

                "target_room": room.name,

                "source_room_id": affected_room.id,

                "source_room": affected_room.name,

                "reservation_conflict_resolved": True,

            },

        )



        plan.actions = [

            PlanAction(

                sequence=1,

                action_type="CREATE_RESERVATION",

                description=(

                    f"Create a reservation for {event.name} "

                    f"in {room.name} for the existing event time."

                ),

                parameters={

                    "event_id": event.id,

                    "room_id": room.id,

                    "start_time": event.start_time.isoformat(),

                    "end_time": event.end_time.isoformat(),

                    "status": "ACTIVE",

                },

                expected_result={

                    "room_id": room.id,

                    "event_id": event.id,

                    "status": "ACTIVE",

                },

                compensation={

                    "action_type": "DELETE_CREATED_RESERVATION",

                    "event_id": event.id,

                    "room_id": room.id,

                },

                status="PENDING",

            ),

            PlanAction(

                sequence=2,

                action_type="CANCEL_RESERVATION",

                description=(

                    f"Cancel the existing {event.name} "

                    f"reservation in {affected_room.name}."

                ),

                parameters={

                    "event_id": event.id,

                    "room_id": affected_room.id,

                    "reason": "Resolve room double booking",

                },

                expected_result={

                    "event_id": event.id,

                    "room_id": affected_room.id,

                    "status": "CANCELLED",

                },

                compensation={

                    "action_type": "RESTORE_RESERVATION",

                    "event_id": event.id,

                    "room_id": affected_room.id,

                },

                status="PENDING",

            ),

        ]



        create_plan(

            db,

            plan,

        )



        plans.append(plan)



        db.commit()



    return plans



def _simulate_equipment_plan(

    db: Session,

    plan: Plan,

    impact: dict,

):

    expected_state = plan.expected_state or {}



    event_id = expected_state.get("event_id")

    equipment_id = expected_state.get("equipment_id")



    quantity = 1



    for action in plan.actions:

        if action.action_type == "ASSIGN_BACKUP_EQUIPMENT":

            parameters = action.parameters or {}

            quantity = int(

                parameters.get("quantity", 1)

            )

            break



    checks = []



    equipment = db.get(

        Equipment,

        equipment_id,

    )



    checks.append(

        {

            "name": "equipment_exists",

            "passed": equipment is not None,

            "details": (

                f"Equipment {equipment.name} exists."

                if equipment is not None

                else f"Equipment {equipment_id} does not exist."

            ),

        }

    )



    if equipment is None:

        result = {

            "success": False,

            "checks": checks,

            "actions": [],

            "final_state": None,

        }



        plan.simulation_result = result

        db.commit()



        return plan



    assignment = db.scalar(

        select(EventEquipment).where(

            EventEquipment.event_id == event_id,

            EventEquipment.equipment_id == equipment_id,

        )

    )



    assignment_exists = assignment is not None



    checks.append(

        {

            "name": "event_equipment_assignment_exists",

            "passed": assignment_exists,

            "details": (

                "Event equipment assignment exists."

                if assignment_exists

                else "Event has no current assignment for this equipment."

            ),

        }

    )



    available_valid = (

        equipment.available_quantity >= quantity

    )



    checks.append(

        {

            "name": "backup_equipment_available",

            "passed": available_valid,

            "details": (

                f"{equipment.available_quantity} available "

                f"unit(s); {quantity} required."

            ),

        }

    )



    current_assigned_quantity = (

        assignment.quantity

        if assignment is not None

        else 0

    )



    expected_original_quantity = expected_state.get(

        "original_assigned_quantity"

    )



    assignment_state_valid = (

        assignment is not None

        and (

            expected_original_quantity is None

            or current_assigned_quantity

            == expected_original_quantity

        )

    )



    checks.append(

        {

            "name": "assignment_state_current",

            "passed": assignment_state_valid,

            "details": (

                "Current assignment matches the planned "

                "pre-execution state."

                if assignment_state_valid

                else (

                    "Current assignment changed since the plan "

                    "was created."

                )

            ),

        }

    )



    expected_assigned_quantity = expected_state.get(

        "expected_assigned_quantity",

        current_assigned_quantity + quantity,

    )



    expected_available_quantity = expected_state.get(

        "expected_available_quantity",

        equipment.available_quantity - quantity,

    )



    simulated_assigned_quantity = (

        current_assigned_quantity + quantity

    )



    simulated_available_quantity = (

        equipment.available_quantity - quantity

    )



    assigned_quantity_valid = (

        simulated_assigned_quantity

        == expected_assigned_quantity

    )



    available_quantity_valid = (

        simulated_available_quantity

        == expected_available_quantity

    )



    checks.append(

        {

            "name": "expected_assigned_quantity",

            "passed": assigned_quantity_valid,

            "details": (

                f"Expected assigned quantity becomes "

                f"{expected_assigned_quantity}."

            ),

        }

    )



    checks.append(

        {

            "name": "expected_available_quantity",

            "passed": available_quantity_valid,

            "details": (

                f"Expected available quantity becomes "

                f"{expected_available_quantity}."

            ),

        }

    )



    action_passed = (

        assignment_exists

        and available_valid

        and assignment_state_valid

        and assigned_quantity_valid

        and available_quantity_valid

    )



    action_result = {

        "sequence": 1,

        "action_type": "ASSIGN_BACKUP_EQUIPMENT",

        "passed": action_passed,

        "details": (

            "Backup equipment can be allocated safely."

            if action_passed

            else "Backup equipment allocation cannot be safely simulated."

        ),

    }



    all_passed = (

        all(check["passed"] for check in checks)

        and action_result["passed"]

    )



    result = {

        "success": all_passed,

        "checks": checks,

        "actions": [action_result],

        "final_state": {

            "event_id": event_id,

            "equipment_id": equipment_id,

            "equipment_name": equipment.name,

            "assigned_quantity": simulated_assigned_quantity,

            "available_quantity": simulated_available_quantity,

            "backup_quantity": quantity,

        },

    }



    plan.simulation_result = result

    db.commit()



    return plan



def simulate_plan(db: Session, plan_id: int):

    plan = get_plan(db, plan_id)



    if plan is None:

        return None



    impact = analyze_incident_impact(db, plan.incident_id)



    if impact is None:

        return None



    event = impact["event"]



    if (

        plan.expected_state

        and plan.expected_state.get("equipment_id")

        is not None

    ):

        return _simulate_equipment_plan(

            db,

            plan,

            impact,

        )



    required_capacity = _get_required_capacity(impact)



    event = impact["event"]

    required_capacity = _get_required_capacity(impact)



    checks = []



    target_room_id = plan.expected_state["target_room_id"]

    source_room_id = plan.expected_state["source_room_id"]



    target_room = db.get(Room, target_room_id)

    source_room = db.get(Room, source_room_id)



    target_exists = target_room is not None



    checks.append(

        {

            "name": "target_room_exists",

            "passed": target_exists,

            "details": (

                f"Target room {target_room.name} exists."

                if target_exists

                else f"Target room {target_room_id} does not exist."

            ),

        }

    )



    if target_room is None:

        result = {

            "success": False,

            "checks": checks,

            "final_state": None,

        }



        plan.simulation_result = result

        db.commit()



        return plan



    capacity_valid = target_room.capacity >= required_capacity



    checks.append(

        {

            "name": "target_room_capacity",

            "passed": capacity_valid,

            "details": (

                f"Room capacity {target_room.capacity} "

                f"meets required capacity {required_capacity}."

            ),

        }

    )



    reservations = list(

        db.scalars(

            select(Reservation)

            .where(Reservation.status == "ACTIVE")

        ).all()

    )



    simulated_reservations = [

        {

            "id": reservation.id,

            "event_id": reservation.event_id,

            "room_id": reservation.room_id,

            "start_time": reservation.start_time,

            "end_time": reservation.end_time,

            "status": reservation.status,

        }

        for reservation in reservations

    ]



    action_results = []





    for action in sorted(plan.actions, key=lambda item: item.sequence):



        if action.action_type == "CREATE_RESERVATION":



            room_id = action.parameters["room_id"]



            conflicts = [

                reservation

                for reservation in simulated_reservations

                if (

                    reservation["room_id"] == room_id

                    and reservation["status"] == "ACTIVE"

                    and _times_overlap(

                        reservation["start_time"],

                        reservation["end_time"],

                        event.start_time,

                        event.end_time,

                    )

                )

            ]



            passed = len(conflicts) == 0



            action_results.append(

                {

                    "sequence": action.sequence,

                    "action_type": action.action_type,

                    "passed": passed,

                    "details": (

                        "No active reservation conflicts with "

                        "the proposed target reservation."

                        if passed

                        else (

                            f"Target room has {len(conflicts)} "

                            f"conflicting active reservation(s)."

                        )

                    ),

                }

            )



            if passed:

                simulated_reservations.append(

                    {

                        "id": None,

                        "event_id": action.parameters["event_id"],

                        "room_id": action.parameters["room_id"],

                        "start_time": event.start_time,

                        "end_time": event.end_time,

                        "status": "ACTIVE",

                    }

                )



        elif action.action_type == "CANCEL_RESERVATION":



            event_id = action.parameters["event_id"]

            room_id = action.parameters["room_id"]



            matching_reservations = [

                reservation

                for reservation in simulated_reservations

                if (

                    reservation["event_id"] == event_id

                    and reservation["room_id"] == room_id

                    and reservation["status"] == "ACTIVE"

                )

            ]



            passed = len(matching_reservations) == 1



            action_results.append(

                {

                    "sequence": action.sequence,

                    "action_type": action.action_type,

                    "passed": passed,

                    "details": (

                        "Existing reservation found and can be cancelled."

                        if passed

                        else (

                            f"Expected exactly one active reservation, "

                            f"found {len(matching_reservations)}."

                        )

                    ),

                }

            )



            if passed:

                matching_reservations[0]["status"] = "CANCELLED"



    target_active_reservations = [

        reservation

        for reservation in simulated_reservations

        if (

            reservation["room_id"] == target_room_id

            and reservation["status"] == "ACTIVE"

            and reservation["event_id"] == event.id

        )

    ]



    source_active_reservations = [

        reservation

        for reservation in simulated_reservations

        if (

            reservation["room_id"] == source_room_id

            and reservation["status"] == "ACTIVE"

            and reservation["event_id"] == event.id

        )

    ]



    target_valid = len(target_active_reservations) == 1

    source_valid = len(source_active_reservations) == 0



    checks.append(

        {

            "name": "target_reservation_created",

            "passed": target_valid,

            "details": (

                "Exactly one active target reservation exists."

                if target_valid

                else "Target reservation state is invalid."

            ),

        }

    )



    checks.append(

        {

            "name": "source_reservation_removed",

            "passed": source_valid,

            "details": (

                "Original source reservation is no longer active."

                if source_valid

                else "Original source reservation is still active."

            ),

        }

    )



    all_passed = all(

        check["passed"]

        for check in checks

    ) and all(

        result["passed"]

        for result in action_results

    )



    result = {

        "success": all_passed,

        "checks": checks,

        "actions": action_results,

        "final_state": {

            "event_id": event.id,

            "event_name": event.name,

            "source_room_id": source_room_id,

            "source_room": source_room.name if source_room else None,

            "target_room_id": target_room_id,

            "target_room": target_room.name,

            "required_capacity": required_capacity,

            "target_capacity": target_room.capacity,

            "target_reservation_active": target_valid,

            "source_reservation_active": not source_valid,

        },

    }



    plan.simulation_result = result



    db.commit()



    return plan



def approve_plan(

    db: Session,

    plan_id: int,

    approved_by_person_id: int,

):

    plan = get_plan(db, plan_id)



    if plan is None:

        return None, "Plan not found"



    if plan.status != "PROPOSED":

        return None, (

            f"Plan cannot be approved from status "

            f"{plan.status}"

        )



    if not plan.simulation_result:

        return None, "Plan must be simulated before approval"



    if not plan.simulation_result.get("success"):

        return None, "Plan simulation did not succeed"



    person = db.get(Person, approved_by_person_id)



    if person is None:

        return None, "Approving person not found"



    plan.status = "APPROVED"

    plan.approved_by_person_id = approved_by_person_id

    plan.approved_at = datetime.now(timezone.utc)



    db.commit()

    db.refresh(plan)



    return plan, None



def _execute_action(

    db: Session,

    action: PlanAction,

) -> dict:

    if action.action_type == "ASSIGN_BACKUP_EQUIPMENT":

        parameters = action.parameters or {}



        event_id = parameters["event_id"]

        equipment_id = parameters["equipment_id"]

        quantity = int(parameters.get("quantity", 1))



        equipment = db.get(

            Equipment,

            equipment_id,

        )



        if equipment is None:

            raise ValueError(

                f"Equipment {equipment_id} not found"

            )



        if equipment.available_quantity < quantity:

            raise ValueError(

                f"Insufficient available equipment. "

                f"Available: {equipment.available_quantity}, "

                f"required: {quantity}"

            )



        assignment = db.scalar(

            select(EventEquipment).where(

                EventEquipment.event_id == event_id,

                EventEquipment.equipment_id == equipment_id,

            )

        )



        if assignment is None:

            assignment = EventEquipment(

                event_id=event_id,

                equipment_id=equipment_id,

                quantity=quantity,

            )

            db.add(assignment)

            created_new_assignment = True

        else:

            assignment.quantity += quantity

            created_new_assignment = False



        equipment.available_quantity -= quantity



        db.flush()



        return {

            "action_type": action.action_type,

            "event_id": event_id,

            "equipment_id": equipment_id,

            "equipment_name": equipment.name,

            "quantity": quantity,

            "status": "ASSIGNED",

            "created_new_assignment": created_new_assignment,

            "remaining_available_quantity": (

                equipment.available_quantity

            ),

            "event_assigned_quantity": assignment.quantity,

        }

    if action.action_type == "CREATE_RESERVATION":

        parameters = action.parameters or {}



        event_id = parameters["event_id"]

        room_id = parameters["room_id"]



        start_time = datetime.fromisoformat(

            parameters["start_time"]

        )

        end_time = datetime.fromisoformat(

            parameters["end_time"]

        )



        existing_conflicts = list(

            db.scalars(

                select(Reservation)

                .where(

                    Reservation.room_id == room_id,

                    Reservation.status == "ACTIVE",

                    Reservation.start_time < end_time,

                    Reservation.end_time > start_time,

                )

            ).all()

        )



        if existing_conflicts:

            raise ValueError(

                f"Target room {room_id} has an active "

                f"reservation conflict."

            )



        reservation = Reservation(

            event_id=event_id,

            room_id=room_id,

            start_time=start_time,

            end_time=end_time,

            status="ACTIVE",

        )



        db.add(reservation)

        db.flush()



        return {

            "action_type": action.action_type,

            "reservation_id": reservation.id,

            "event_id": event_id,

            "room_id": room_id,

            "start_time": reservation.start_time.isoformat(),

            "end_time": reservation.end_time.isoformat(),

            "status": reservation.status,

        }



    if action.action_type == "CANCEL_RESERVATION":

        parameters = action.parameters or {}



        event_id = parameters["event_id"]

        room_id = parameters["room_id"]



        reservations = list(

            db.scalars(

                select(Reservation)

                .where(

                    Reservation.event_id == event_id,

                    Reservation.room_id == room_id,

                    Reservation.status == "ACTIVE",

                )

            ).all()

        )



        if len(reservations) != 1:

            raise ValueError(

                f"Expected exactly one active reservation "

                f"for event {event_id} in room {room_id}, "

                f"found {len(reservations)}."

            )



        reservation = reservations[0]

        reservation.status = "CANCELLED"



        db.flush()



        return {

            "action_type": action.action_type,

            "reservation_id": reservation.id,

            "event_id": event_id,

            "room_id": room_id,

            "status": "CANCELLED",

        }



    raise ValueError(

        f"Unsupported action type: {action.action_type}"

    )



def commit_plan(

    db: Session,

    plan_id: int,

):

    plan = get_plan(db, plan_id)



    if plan is None:

        return None, "Plan not found"



    if plan.status != "APPROVED":

        return None, (

            f"Plan cannot be executed from status "

            f"{plan.status}"

        )



    if not plan.simulation_result:

        return None, "Plan must be simulated before execution"



    if not plan.simulation_result.get("success"):

        return None, "Plan simulation did not succeed"



    execution = Execution(

        plan_id=plan.id,

        execution_type="ORIGINAL",

        status="RUNNING",

        started_at=datetime.now(timezone.utc),

    )



    create_execution(db, execution)



    plan.status = "EXECUTING"



    db.commit()

    db.refresh(execution)



    action_results = []



    for action in sorted(

        plan.actions,

        key=lambda item: item.sequence,

    ):

        try:

            action.status = "EXECUTING"

            db.commit()



            result = _execute_action(

                db,

                action,

            )



            action.status = "EXECUTED"



            action_results.append(

                {

                    "sequence": action.sequence,

                    "action_id": action.id,

                    "action_type": action.action_type,

                    "status": "EXECUTED",

                    "result": result,

                }

            )



            db.commit()



        except Exception as exc:

            db.rollback()



            failed_action = db.get(

                PlanAction,

                action.id,

            )



            failed_execution = db.get(

                Execution,

                execution.id,

            )



            failed_plan = db.get(

                Plan,

                plan.id,

            )



            failed_action.status = "FAILED"



            failed_execution.status = "FAILED"

            failed_execution.error_message = str(exc)

            failed_execution.completed_at = (

                datetime.now(timezone.utc)

            )

            failed_execution.result = {

                "success": False,

                "actions": action_results,

                "failed_action": {

                    "sequence": action.sequence,

                    "action_id": action.id,

                    "action_type": action.action_type,

                    "error": str(exc),

                },

            }



            failed_plan.status = "FAILED"



            db.commit()



            return failed_execution, None



    execution.status = "SUCCEEDED"

    execution.completed_at = datetime.now(timezone.utc)



    execution.result = {

        "success": True,

        "actions": action_results,

    }



    plan.status = "EXECUTED"



    db.commit()

    db.refresh(execution)



    return execution, None



def _verify_equipment_execution(

    db: Session,

    execution: Execution,

    plan: Plan,

):

    expected_state = plan.expected_state or {}



    event_id = expected_state.get("event_id")

    equipment_id = expected_state.get("equipment_id")



    expected_assigned_quantity = expected_state.get(

        "expected_assigned_quantity"

    )



    expected_available_quantity = expected_state.get(

        "expected_available_quantity"

    )



    equipment = db.get(

        Equipment,

        equipment_id,

    )



    assignment = db.scalar(

        select(EventEquipment).where(

            EventEquipment.event_id == event_id,

            EventEquipment.equipment_id == equipment_id,

        )

    )



    checks = []



    equipment_exists = equipment is not None



    checks.append(

        {

            "name": "equipment_exists",

            "passed": equipment_exists,

            "details": (

                "Equipment exists."

                if equipment_exists

                else "Equipment no longer exists."

            ),

        }

    )



    actual_assigned_quantity = (

        assignment.quantity

        if assignment is not None

        else 0

    )



    assigned_quantity_matches = (

        assignment is not None

        and actual_assigned_quantity

        == expected_assigned_quantity

    )



    checks.append(

        {

            "name": "event_equipment_assignment",

            "passed": assigned_quantity_matches,

            "details": (

                f"Event has {actual_assigned_quantity} assigned "

                f"unit(s); expected "

                f"{expected_assigned_quantity}."

            ),

        }

    )



    actual_available_quantity = (

        equipment.available_quantity

        if equipment is not None

        else None

    )



    available_quantity_matches = (

        actual_available_quantity

        == expected_available_quantity

    )



    checks.append(

        {

            "name": "equipment_inventory",

            "passed": available_quantity_matches,

            "details": (

                f"Inventory has {actual_available_quantity} "

                f"available unit(s); expected "

                f"{expected_available_quantity}."

            ),

        }

    )



    success = all(

        check["passed"]

        for check in checks

    )



    verification_result = {

        "success": success,

        "checks": checks,

        "expected_state": expected_state,

        "actual_state": {

            "event_id": event_id,

            "equipment_id": equipment_id,

            "equipment_name": (

                equipment.name

                if equipment is not None

                else None

            ),

            "assigned_quantity": actual_assigned_quantity,

            "available_quantity": actual_available_quantity,

        },

    }



    execution.result = {

        **(execution.result or {}),

        "verification": verification_result,

    }



    if success:

        execution.status = "VERIFIED"

        plan.status = "VERIFIED"

    else:

        execution.status = "VERIFICATION_FAILED"

        plan.status = "FAILED"



        db.commit()

        db.refresh(execution)



    return execution, None



def verify_execution(

    db: Session,

    execution_id: int,

):

    execution = get_execution(db, execution_id)



    if execution is None:

        return None, "Execution not found"



    if execution.status == "VERIFIED":

        return execution, None



    if execution.status != "SUCCEEDED":

        return None, (

            f"Execution cannot be verified from status "

            f"{execution.status}"

        )



    plan = get_plan(db, execution.plan_id)



    if plan is None:

        return None, "Plan not found"



    if (

        plan.expected_state

        and plan.expected_state.get("equipment_id")

        is not None

    ):

        return _verify_equipment_execution(

            db,

            execution,

            plan,

        )



    if plan.status != "EXECUTED":

        return None, (

            f"Plan cannot be verified from status "

            f"{plan.status}"

        )



    expected_state = plan.expected_state or {}



    event_id = expected_state.get("event_id")

    source_room_id = expected_state.get("source_room_id")

    target_room_id = expected_state.get("target_room_id")



    if (

        event_id is None

        or source_room_id is None

        or target_room_id is None

    ):

        return None, "Plan expected state is incomplete"



    event = db.get(

        Event,

        event_id,

    )



    if event is None:

        return None, "Event not found"



    target_reservations = list(

        db.scalars(

            select(Reservation)

            .where(

                Reservation.event_id == event_id,

                Reservation.room_id == target_room_id,

                Reservation.status == "ACTIVE",

            )

        ).all()

    )



    source_reservations = list(

        db.scalars(

            select(Reservation)

            .where(

                Reservation.event_id == event_id,

                Reservation.room_id == source_room_id,

                Reservation.status == "ACTIVE",

            )

        ).all()

    )



    target_conflicts = list(

        db.scalars(

            select(Reservation)

            .where(

                Reservation.room_id == target_room_id,

                Reservation.status == "ACTIVE",

                Reservation.start_time < event.end_time,

                Reservation.end_time > event.start_time,

            )

        ).all()

    )



    target_conflicts = [

        reservation

        for reservation in target_conflicts

        if reservation.event_id != event_id

    ]



    checks = []



    target_correct = len(target_reservations) == 1



    checks.append(

        {

            "name": "target_reservation_active",

            "passed": target_correct,

            "details": (

                "Exactly one active target reservation exists."

                if target_correct

                else (

                    f"Expected one active target reservation, "

                    f"found {len(target_reservations)}."

                )

            ),

        }

    )



    source_removed = len(source_reservations) == 0



    checks.append(

        {

            "name": "source_reservation_cancelled",

            "passed": source_removed,

            "details": (

                "Original source reservation is no longer active."

                if source_removed

                else (

                    f"Found {len(source_reservations)} "

                    "active source reservation(s)."

                )

            ),

        }

    )



    no_target_conflict = len(target_conflicts) == 0



    checks.append(

        {

            "name": "target_room_has_no_conflict",

            "passed": no_target_conflict,

            "details": (

                "Target room has no overlapping active reservations."

                if no_target_conflict

                else (

                    f"Target room has {len(target_conflicts)} "

                    "overlapping active reservation(s)."

                )

            ),

        }

    )



    success = all(

        check["passed"]

        for check in checks

    )



    verification_result = {

        "success": success,

        "checks": checks,

        "expected_state": expected_state,

        "actual_state": {

            "event_id": event_id,

            "source_room_id": source_room_id,

            "target_room_id": target_room_id,

            "target_reservation_count": len(target_reservations),

            "source_active_reservation_count": len(

                source_reservations

            ),

            "target_conflict_count": len(

                target_conflicts

            ),

        },

    }



    execution.result = {

        **(execution.result or {}),

        "verification": verification_result,

    }



    if success:

        execution.status = "VERIFIED"

        plan.status = "VERIFIED"

    else:

        execution.status = "VERIFICATION_FAILED"

        plan.status = "FAILED"



        db.commit()

        db.refresh(execution)



    return execution, None



def _compensate_action(

    db: Session,

    action: PlanAction,

    execution_action_result: dict,

) -> dict:

    compensation = action.compensation or {}

    compensation_type = compensation.get("action_type")



    if compensation_type == "DELETE_CREATED_RESERVATION":

        reservation_id = execution_action_result.get(

            "reservation_id"

        )



        if reservation_id is None:

            raise ValueError(

                "Created reservation ID is missing"

            )



        reservation = db.get(

            Reservation,

            reservation_id,

        )



        if reservation is None:

            raise ValueError(

                f"Reservation {reservation_id} not found"

            )



        reservation.status = "CANCELLED"

        db.flush()



        return {

            "action_type": compensation_type,

            "reservation_id": reservation_id,

            "status": "CANCELLED",

        }



    if compensation_type == "RESTORE_RESERVATION":

        start_time = datetime.fromisoformat(

            execution_action_result["start_time"]

        )



        end_time = datetime.fromisoformat(

            execution_action_result["end_time"]

        )



        reservation = Reservation(

            event_id=execution_action_result["event_id"],

            room_id=execution_action_result["room_id"],

            start_time=start_time,

            end_time=end_time,

            status="ACTIVE",

        )



        db.add(reservation)

        db.flush()



        return {

            "action_type": compensation_type,

            "reservation_id": reservation.id,

            "event_id": reservation.event_id,

            "room_id": reservation.room_id,

            "status": "ACTIVE",

        }



    raise ValueError(

        f"Unsupported compensation type: {compensation_type}"

    )



def recover_execution(

    db: Session,

    execution_id: int,

):

    execution = get_execution(

        db,

        execution_id,

    )



    if execution is None:

        return None, "Execution not found"



    if execution.status != "FAILED":

        return None, (

            f"Execution cannot be recovered from status "

            f"{execution.status}"

        )



    plan = get_plan(

        db,

        execution.plan_id,

    )



    if plan is None:

        return None, "Plan not found"



    plan.status = "RECOVERING"



    recovery_execution = Execution(

        plan_id=plan.id,

        execution_type="RECOVERY",

        status="RUNNING",

        started_at=datetime.now(timezone.utc),

    )



    create_execution(

        db,

        recovery_execution,

    )



    db.commit()



    successful_actions = [

        item

        for item in (execution.result or {}).get("actions", [])

        if item.get("status") == "EXECUTED"

    ]



    recovery_results = []



    try:

        for action_result in reversed(successful_actions):

            action_id = action_result["action_id"]



            action = db.get(

                PlanAction,

                action_id,

            )



            if action is None:

                raise ValueError(

                    f"Plan action {action_id} not found"

                )



            compensation_result = _compensate_action(

                db,

                action,

                action_result["result"],

            )



            recovery_results.append(

                {

                    "sequence": action.sequence,

                    "action_id": action.id,

                    "action_type": action.action_type,

                    "compensation": compensation_result,

                }

            )



        recovery_execution.status = "SUCCEEDED"

        recovery_execution.result = {

            "success": True,

            "compensated_actions": recovery_results,

        }

        recovery_execution.completed_at = (

            datetime.now(timezone.utc)

        )



        plan.status = "RECOVERED"



        db.commit()

        db.refresh(recovery_execution)



        return recovery_execution, None



    except Exception as exc:

        db.rollback()



        recovery_execution = db.get(

            Execution,

            recovery_execution.id,

        )



        plan = db.get(

            Plan,

            plan.id,

        )



        recovery_execution.status = "FAILED"

        recovery_execution.error_message = str(exc)

        recovery_execution.result = {

            "success": False,

            "compensated_actions": recovery_results,

        }

        recovery_execution.completed_at = (

            datetime.now(timezone.utc)

        )



        plan.status = "RECOVERY_FAILED"



        db.commit()



        return recovery_execution, None