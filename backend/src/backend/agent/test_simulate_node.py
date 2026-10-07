from backend.agent.graph import simulate_node


def main():
    state = {
        "candidate_plans": [
            {
                "plan_id": 2,
                "incident_id": 2,
                "summary": (
                    "Move Robotics Final "
                    "from C-204 to C-301"
                ),
                "risk_level": "LOW",
            },
            {
                "plan_id": 3,
                "incident_id": 2,
                "summary": (
                    "Move Robotics Final "
                    "from C-204 to Main Auditorium"
                ),
                "risk_level": "LOW",
            },
        ]
    }

    result = simulate_node(state)

    print("Simulated plans:")

    for plan in result["simulated_plans"]:
        print()
        print(
            f"Plan {plan['plan_id']}: "
            f"{plan['summary']}"
        )
        print(
            f"Simulation success: "
            f"{plan['simulation_success']}"
        )
        print(
            f"Simulation result: "
            f"{plan['simulation_result']}"
        )


if __name__ == "__main__":
    main()