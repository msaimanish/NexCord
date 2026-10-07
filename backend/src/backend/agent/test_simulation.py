from backend.database import SessionLocal
from backend.services.plan_service import simulate_plan

def main():
    db = SessionLocal()

    try:
        for plan_id in [2, 3]:
            plan = simulate_plan(
                db,
                plan_id,
            )

            if plan is None:
                print(
                    f"Plan {plan_id}: NOT FOUND"
                )
                continue

            print(f"\nPlan {plan_id}")
            print(
                f"Summary: {plan.summary}"
            )

            print(
                f"Simulation: "
                f"{plan.simulation_result}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()