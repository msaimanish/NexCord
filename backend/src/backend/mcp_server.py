from mcp.server import MCPServer
from backend.database import SessionLocal
from backend.services.event_service import get_event_operational_state
from datetime import datetime
from backend.services.vendor_service import (
    check_vendor_availability,
    get_vendor,
)
from backend.services.room_service import find_available_rooms
from backend.services.incident_service import (
    get_incident as get_incident_service,
)
from backend.services.reservation_service import (
    find_conflicting_reservations,
)
from backend.services.incident_service import (
    analyze_incident_impact,
)
from backend.services.plan_service import (
    simulate_plan as simulate_existing_plan,
)
from backend.repositories.plan_repository import get_plan
from backend.services.plan_service import (
    commit_plan as commit_existing_plan,
)
from backend.services.plan_service import (
    verify_execution as verify_existing_execution,
    recover_execution as recover_existing_execution,
)
from backend.services.knowledge_service import (
    query_knowledge as query_knowledge_service,
)



mcp = MCPServer(
    "NexCord MCP",
)

def serialize_room(room) -> dict:
    return {
        "id": room.id,
        "venue_id": room.venue_id,
        "name": room.name,
        "capacity": room.capacity,
        "floor": room.floor,
        "status": room.status,
    }

def serialize_vendor(vendor) -> dict:
    return {
        "id": vendor.id,
        "name": vendor.name,
        "vendor_type": vendor.vendor_type,
        "contact_name": vendor.contact_name,
        "phone": vendor.phone,
        "email": vendor.email,
        "status": vendor.status,
    }

def serialize_incident(incident) -> dict:
    return {
        "id": incident.id,
        "event_id": incident.event_id,
        "room_id": incident.room_id,
        "vendor_id": incident.vendor_id,
        "person_id": incident.person_id,
        "equipment_id": incident.equipment_id,
        "type": incident.type,
        "severity": incident.severity,
        "status": incident.status,
        "source": incident.source,
        "title": incident.title,
        "description": incident.description,
        "extra_data": incident.extra_data,
        "detected_at": (
            incident.detected_at.isoformat()
            if incident.detected_at
            else None
        ),
        "resolved_at": (
            incident.resolved_at.isoformat()
            if incident.resolved_at
            else None
        ),
    }

@mcp.tool()
def ping() -> dict:
    """Check whether the NexCord MCP server is running."""
    return {
        "status": "ok",
        "service": "nexcord-mcp",
    }




def serialize_event_state(state: dict) -> dict:
    event = state["event"]

    return {
        "event": {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "status": event.status,
        },
        "reservations": [
            {
                "reservation": {
                    "id": item["reservation"].id,
                    "event_id": item["reservation"].event_id,
                    "room_id": item["reservation"].room_id,
                    "start_time": item["reservation"].start_time.isoformat(),
                    "end_time": item["reservation"].end_time.isoformat(),
                    "status": item["reservation"].status,
                },
                "room": (
                    {
                        "id": item["room"].id,
                        "venue_id": item["room"].venue_id,
                        "name": item["room"].name,
                        "capacity": item["room"].capacity,
                        "floor": item["room"].floor,
                        "status": item["room"].status,
                    }
                    if item["room"] is not None
                    else None
                ),
            }
            for item in state["reservations"]
        ],
        "conflicting_reservations": [
            {
                "id": reservation.id,
                "event_id": reservation.event_id,
                "room_id": reservation.room_id,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
                "status": reservation.status,
            }
            for reservation in state["conflicting_reservations"]
        ],
        "incidents": [
            {
                "id": incident.id,
                "event_id": incident.event_id,
                "type": incident.type,
                "severity": incident.severity,
                "status": incident.status,
                "title": incident.title,
                "description": incident.description,
            }
            for incident in state["incidents"]
        ],
        "assigned_people": [
            {
                "person": {
                    "id": item["person"].id,
                    "name": item["person"].name,
                    "role": item["person"].role,
                    "email": item["person"].email,
                    "phone": item["person"].phone,
                },
                "assignment_role": item["assignment_role"],
            }
            for item in state["assigned_people"]
        ],
        "assigned_vendors": [
            {
                "vendor": {
                    "id": item["vendor"].id,
                    "name": item["vendor"].name,
                    "vendor_type": item["vendor"].vendor_type,
                    "contact_name": item["vendor"].contact_name,
                    "phone": item["vendor"].phone,
                    "email": item["vendor"].email,
                    "status": item["vendor"].status,
                },
                "service_type": item["service_type"],
                "status": item["status"],
            }
            for item in state["assigned_vendors"]
        ],
        "assigned_equipment": [
            {
                "equipment": {
                    "id": item["equipment"].id,
                    "name": item["equipment"].name,
                    "category": item["equipment"].category,
                    "quantity": item["equipment"].quantity,
                    "available_quantity": item["equipment"].available_quantity,
                    "status": item["equipment"].status,
                },
                "quantity": item["quantity"],
            }
            for item in state["assigned_equipment"]
        ],
        "open_incident_count": state["open_incident_count"],
        "state_facts": state["state_facts"],
    }

@mcp.tool()
def get_event_state(event_id: int) -> dict:
    """Return the current operational state of an event."""

    db = SessionLocal()

    try:
        state = get_event_operational_state(
            db,
            event_id,
        )

        if state is None:
            return {
                "error": "Event not found",
                "event_id": event_id,
            }

        return serialize_event_state(state)

    finally:
        db.close()


@mcp.tool()
def get_available_rooms(
    start_time: str,
    end_time: str,
    required_capacity: int,
) -> dict:
    """Return rooms available for the requested time and capacity."""

    db = SessionLocal()

    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        rooms = find_available_rooms(
            db,
            start,
            end,
            required_capacity,
        )

        return {
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "required_capacity": required_capacity,
            "rooms": [
                serialize_room(room)
                for room in rooms
            ],
        }

    finally:
        db.close()

@mcp.tool()
def get_vendor_status(
    vendor_id: int,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict:
    """Return a vendor's current status and optional time-window availability."""

    db = SessionLocal()

    try:
        vendor = get_vendor(
            db,
            vendor_id,
        )

        if vendor is None:
            return {
                "error": "Vendor not found",
                "vendor_id": vendor_id,
            }

        result = {
            "vendor": serialize_vendor(vendor),
        }

        if start_time is not None or end_time is not None:
            if start_time is None or end_time is None:
                return {
                    "error": "start_time and end_time must be provided together",
                    "vendor_id": vendor_id,
                }

            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)

            availability = check_vendor_availability(
                db,
                vendor_id,
                start,
                end,
            )

            result["availability"] = {
                **availability,
                "requested_start": availability["requested_start"].isoformat(),
                "requested_end": availability["requested_end"].isoformat(),
                "conflicts": [
                    {
                        **conflict,
                        "start_time": conflict["start_time"].isoformat(),
                        "end_time": conflict["end_time"].isoformat(),
                    }
                    for conflict in availability["conflicts"]
                ],
            }

        return result

    finally:
        db.close()

@mcp.tool()
def get_incident(
    incident_id: int,
) -> dict:
    """Return details of a specific event incident."""

    db = SessionLocal()

    try:
        incident = get_incident_service(
            db,
            incident_id,
        )

        if incident is None:
            return {
                "error": "Incident not found",
                "incident_id": incident_id,
            }

        return {
            "incident": serialize_incident(incident),
        }

    finally:
        db.close()

@mcp.tool()
def detect_conflicts(
    room_id: int,
    start_time: str,
    end_time: str,
) -> dict:
    """Detect active reservation conflicts for a room and time window."""

    db = SessionLocal()

    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        conflicts = find_conflicting_reservations(
            db,
            room_id,
            start,
            end,
        )

        return {
            "room_id": room_id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "conflict_count": len(conflicts),
            "has_conflicts": bool(conflicts),
            "conflicts": [
                {
                    "reservation_id": reservation.id,
                    "event_id": reservation.event_id,
                    "room_id": reservation.room_id,
                    "start_time": reservation.start_time.isoformat(),
                    "end_time": reservation.end_time.isoformat(),
                    "status": reservation.status,
                }
                for reservation in conflicts
            ],
        }

    except ValueError as exc:
        return {
            "error": str(exc),
            "room_id": room_id,
        }

    finally:
        db.close()

def serialize_impact(impact: dict) -> dict:
    incident = impact["incident"]
    event = impact["event"]
    room = impact["affected_room"]
    vendor = impact["affected_vendor"]
    person = impact["affected_person"]
    equipment = impact["affected_equipment"]

    return {
        "incident": serialize_incident(incident),

        "event": {
            "id": event.id,
            "name": event.name,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "status": event.status,
        },

        "affected_room": (
            {
                "id": room.id,
                "name": room.name,
                "capacity": room.capacity,
                "floor": room.floor,
                "status": room.status,
            }
            if room is not None
            else None
        ),

        "affected_vendor": (
            serialize_vendor(vendor)
            if vendor is not None
            else None
        ),

        "affected_person": (
            {
                "id": person.id,
                "name": person.name,
                "role": person.role,
                "email": person.email,
                "phone": person.phone,
            }
            if person is not None
            else None
        ),

        "affected_equipment": (
            {
                "id": equipment.id,
                "name": equipment.name,
                "category": equipment.category,
                "quantity": equipment.quantity,
                "available_quantity": equipment.available_quantity,
                "status": equipment.status,
            }
            if equipment is not None
            else None
        ),

        "active_reservations": [
            {
                "id": reservation.id,
                "event_id": reservation.event_id,
                "room_id": reservation.room_id,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
                "status": reservation.status,
            }
            for reservation in impact["active_reservations"]
        ],

        "conflicting_reservations": [
            {
                "id": reservation.id,
                "event_id": reservation.event_id,
                "room_id": reservation.room_id,
                "start_time": reservation.start_time.isoformat(),
                "end_time": reservation.end_time.isoformat(),
                "status": reservation.status,
            }
            for reservation in impact["conflicting_reservations"]
        ],

        "assigned_people": [
            {
                "person": {
                    "id": item["person"].id,
                    "name": item["person"].name,
                    "role": item["person"].role,
                },
                "assignment_role": item["assignment_role"],
            }
            for item in impact["assigned_people"]
        ],

        "assigned_vendors": [
            {
                "vendor": {
                    "id": item["vendor"].id,
                    "name": item["vendor"].name,
                    "vendor_type": item["vendor"].vendor_type,
                    "status": item["vendor"].status,
                },
                "service_type": item["service_type"],
                "status": item["status"],
            }
            for item in impact["assigned_vendors"]
        ],

        "assigned_equipment": [
            {
                "equipment": {
                    "id": item["equipment"].id,
                    "name": item["equipment"].name,
                    "category": item["equipment"].category,
                    "status": item["equipment"].status,
                },
                "quantity": item["quantity"],
            }
            for item in impact["assigned_equipment"]
        ],

        "impact_facts": impact["impact_facts"],
    }

@mcp.tool()
def analyze_impact(
    incident_id: int,
) -> dict:
    """Analyze the operational impact of an incident."""

    db = SessionLocal()

    try:
        impact = analyze_incident_impact(
            db,
            incident_id,
        )

        if impact is None:
            return {
                "error": "Incident not found",
                "incident_id": incident_id,
            }

        return serialize_impact(impact)

    finally:
        db.close()


@mcp.tool()
def simulate_plan(
    plan_id: int,
) -> dict:
    """Simulate a proposed NexCord plan without executing it."""

    db = SessionLocal()

    try:
        plan = get_plan(
            db,
            plan_id,
        )

        if plan is None:
            return {
                "error": "Plan not found",
                "plan_id": plan_id,
            }

        simulated_plan = simulate_existing_plan(
            db,
            plan_id,
        )

        if simulated_plan is None:
            return {
                "error": "Unable to simulate plan",
                "plan_id": plan_id,
            }

        return {
            "plan_id": simulated_plan.id,
            "incident_id": simulated_plan.incident_id,
            "summary": simulated_plan.summary,
            "status": simulated_plan.status,
            "simulation_result": simulated_plan.simulation_result,
            "expected_state": simulated_plan.expected_state,
        }

    finally:
        db.close()

def serialize_execution(execution) -> dict:
    return {
        "id": execution.id,
        "plan_id": execution.plan_id,
        "execution_type": execution.execution_type,
        "status": execution.status,
        "result": execution.result,
        "error_message": execution.error_message,
        "started_at": (
            execution.started_at.isoformat()
            if execution.started_at
            else None
        ),
        "completed_at": (
            execution.completed_at.isoformat()
            if execution.completed_at
            else None
        ),
        "created_at": execution.created_at.isoformat(),
    }

@mcp.tool()
def commit_plan(
    plan_id: int,
) -> dict:
    """Execute an approved NexCord plan."""

    db = SessionLocal()

    try:
        execution, error = commit_existing_plan(
            db,
            plan_id,
        )

        if execution is None:
            return {
                "success": False,
                "plan_id": plan_id,
                "error": error,
            }

        return {
            "success": execution.status == "SUCCEEDED",
            "execution": serialize_execution(execution),
        }

    finally:
        db.close()

@mcp.tool()
def verify_execution(
    execution_id: int,
) -> dict:
    """Verify that an executed NexCord plan produced the expected state."""

    db = SessionLocal()

    try:
        execution, error = verify_existing_execution(
            db,
            execution_id,
        )

        if execution is None:
            return {
                "success": False,
                "execution_id": execution_id,
                "error": error,
            }

        return {
            "success": execution.status == "VERIFIED",
            "execution": serialize_execution(execution),
        }

    finally:
        db.close()

@mcp.tool()
def recover_execution(
    execution_id: int,
) -> dict:
    """Recover a failed NexCord execution using compensating actions."""

    db = SessionLocal()

    try:
        recovery, error = recover_existing_execution(
            db,
            execution_id,
        )

        if recovery is None:
            return {
                "success": False,
                "execution_id": execution_id,
                "error": error,
            }

        return {
            "success": recovery.status == "SUCCEEDED",
            "recovery": serialize_execution(recovery),
        }

    finally:
        db.close()


@mcp.tool()
def query_knowledge(
    query: str,
    top_k: int = 3,
) -> dict:
    """Search NexCord operational knowledge using semantic similarity."""

    db = SessionLocal()

    try:
        return query_knowledge_service(
            db,
            query,
            top_k,
        )

    except ValueError as exc:
        return {
            "error": str(exc),
        }

    finally:
        db.close()

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )