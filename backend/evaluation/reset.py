from backend.database import SessionLocal
from backend.models import (
    OperationalObservation,
    Plan,
    PlanAction,
    Reservation,
)


def reset_plans(
    db,
    evaluation_plan_ids: list[int],
) -> None:
    """Reset reusable evaluation plans and their actions."""
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

    db.query(PlanAction).filter(
        PlanAction.plan_id.in_(evaluation_plan_ids)
    ).update(
        {
            PlanAction.status: "PENDING",
        },
        synchronize_session=False,
    )


def reset_room_double_booking_fixture(
    event_id: int,
    source_reservation_id: int,
    evaluation_plan_ids: list[int],
) -> None:
    """Reset the database to the room double-booking evaluation state."""
    db = SessionLocal()

    try:
        # Restore the original reservation.
        db.query(Reservation).filter(
            Reservation.id == source_reservation_id
        ).update(
            {
                Reservation.status: "ACTIVE",
            },
            synchronize_session=False,
        )

        # Cancel every other reservation belonging to this event.
        # These are considered evaluation-created/replacement reservations.
        db.query(Reservation).filter(
            Reservation.event_id == event_id,
            Reservation.id != source_reservation_id,
        ).update(
            {
                Reservation.status: "CANCELLED",
            },
            synchronize_session=False,
        )

        # Reset reusable evaluation plans and actions.
        reset_plans(
            db,
            evaluation_plan_ids,
        )

        db.commit()

    finally:
        db.close()


def inject_room_double_booking_failure(
    source_reservation_id: int,
) -> None:
    """Inject an external failure for the recovery evaluation.

    The source reservation is cancelled before the graph resumes,
    causing the second action of the room-move plan to fail.
    """
    db = SessionLocal()

    try:
        db.query(Reservation).filter(
            Reservation.id == source_reservation_id
        ).update(
            {
                Reservation.status: "CANCELLED",
            },
            synchronize_session=False,
        )

        db.commit()

    finally:
        db.close()


def reset_crowding_fixture(
    event_id: int,
    source_reservation_id: int,
    evaluation_plan_ids: list[int],
) -> None:
    """Reset the database to the crowding evaluation state."""
    db = SessionLocal()

    try:
        # Restore the original AI Workshop reservation.
        db.query(Reservation).filter(
            Reservation.id == source_reservation_id
        ).update(
            {
                Reservation.status: "ACTIVE",
            },
            synchronize_session=False,
        )

        # Cancel every replacement reservation created for this event.
        db.query(Reservation).filter(
            Reservation.event_id == event_id,
            Reservation.id != source_reservation_id,
        ).update(
            {
                Reservation.status: "CANCELLED",
            },
            synchronize_session=False,
        )

        # Reset reusable crowding evaluation plans and actions.
        reset_plans(
            db,
            evaluation_plan_ids,
        )

        # Ensure the event has the operational observation
        # required by the ML risk service.
        observation = (
            db.query(OperationalObservation)
            .filter(
                OperationalObservation.event_id == event_id
            )
            .order_by(
                OperationalObservation.id.desc()
            )
            .first()
        )

        if observation is None:
            observation = OperationalObservation(
                event_id=event_id,
                occupancy_ratio=1.0166667,
                queue_length=0,
                event_delay_minutes=0,
                vendor_delay_minutes=0,
                equipment_failure_count=0,
                source="COMPUTER_VISION",
            )

            db.add(observation)

        else:
            observation.occupancy_ratio = 1.0166667
            observation.queue_length = 0
            observation.event_delay_minutes = 0
            observation.vendor_delay_minutes = 0
            observation.equipment_failure_count = 0
            observation.source = "COMPUTER_VISION"

        db.commit()

    finally:
        db.close()

