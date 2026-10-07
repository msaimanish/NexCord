from backend.agent.graph import generate_plans_node


def main():
    state = {
        "detected_problems": [
            {
                "incident_id": 2,
                "type": "ROOM_DOUBLE_BOOKED",
            }
        ]
    }

    result = generate_plans_node(state)

    print("Candidate plans:")

    for plan in result["candidate_plans"]:
        print()
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Summary: {plan['summary']}")
        print(f"Risk: {plan['risk_level']}")
        print(
            f"Estimated delay: "
            f"{plan['estimated_delay_minutes']} minutes"
        )

        print("Actions:")

        for action in plan["actions"]:
            print(
                f"  {action['sequence']}. "
                f"{action['action_type']}: "
                f"{action['description']}"
            )


if __name__ == "__main__":
    main()