from backend.agent.graph import (
    build_graph,
)
from langgraph.types import Command

from backend.agent.graph import build_graph

def main() -> None:
    graph = build_graph()

    initial_state = {
        "user_request": (
            "Are there any problems with "
            "the Robotics Final?"
        ),
        "event_id": 3,
        "approved_by_person_id": 1,
    }

    config = {
        "configurable": {
            "thread_id": "robotics-final-test-1"
        }
    }



    result = graph.invoke(
        initial_state,
        config=config,
    )

    print("Initial graph result:")
    print(result)

    interrupts = result.get("__interrupt__", [])

    if not interrupts:
        print("Graph did not pause for approval.")
        return

    print()
    print("Approval request:")
    print(interrupts[0].value)

    print()
    decision = input("Approve execution? [y/N]: ").strip().lower()

    approved = decision == "y"

    result = graph.invoke(
        Command(resume=approved),
        config=config,
    )

    print()
    print("Final graph result:")
    print(result)


if __name__ == "__main__":
    main()