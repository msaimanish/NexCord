from backend.database import SessionLocal
from backend.models import Plan, PlanAction, Reservation


DEFAULT_EVENT_ID = 3
DEFAULT_SOURCE_RESERVATION_ID = 3

DEFAULT_EVALUATION_PLAN_IDS = [
    4,
    5,
    6,
]


def reset_room_double_booking_fixture(
    event_id: int = DEFAULT_EVENT_ID,
    source_reservation_id: int = DEFAULT_SOURCE_RESERVATION_ID,
    evaluation_plan_ids: list[int] = DEFAULT_EVALUATION_PLAN_IDS,
) -> None:
    db = SessionLocal()

    try:
        # Restore the original Robotics Final reservation.
        db.query(Reservation).filter(
            Reservation.id == source_reservation_id
        ).update(
            {
                Reservation.status: "ACTIVE",
            },
            synchronize_session=False,
        )

        # Any other reservation for this evaluation event
        # is considered an evaluation-created/replacement
        # reservation and must not remain active.
        db.query(Reservation).filter(
            Reservation.event_id == event_id,
            Reservation.id != source_reservation_id,
        ).update(
            {
                Reservation.status: "CANCELLED",
            },
            synchronize_session=False,
        )

        # Reset reusable evaluation plans.
        db.query(Plan).filter(
            Plan.id.in_(evaluation_plan_ids)
        ).update(
            {
                Plan.status: "PROPOSED",
                Plan.simulation_result: None,
                Plan.approved_by_person_id: None,
                Plan.approved_at: None,
            },
            synchronize_session=False,
        )

        # Reset their action execution state.
        db.query(PlanAction).filter(
            PlanAction.plan_id.in_(evaluation_plan_ids)
        ).update(
            {
                PlanAction.status: "PENDING",
            },
            synchronize_session=False,
        )

        db.commit()

    finally:
        db.close()
