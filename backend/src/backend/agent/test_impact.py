from backend.agent.graph import analyze_impact_node


def main():
    state = {
        "detected_problems": [
            {
                "incident_id": 2,
            },
            {
                "incident_id": 3,
            },
            {
                "incident_id": 4,
            },
            {
                "incident_id": 5,
            },
        ]
    }

    result = analyze_impact_node(state)

    for impact in result["incident_impacts"]:
        print(impact)
        print()


if __name__ == "__main__":
    main()