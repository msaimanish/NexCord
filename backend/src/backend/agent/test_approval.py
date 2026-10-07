from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from backend.agent.graph import approval_node
from backend.agent.state import AgentState


def main() -> None:
    builder = StateGraph(AgentState)

    builder.add_node(
        "approval",
        approval_node,
    )

    builder.add_edge(
        START,
        "approval",
    )

    builder.add_edge(
        "approval",
        END,
    )

    checkpointer = MemorySaver()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": "approval-test-1"
        }
    }

    initial_state = {
        "selected_plan": {
            "plan_id": 999,
            "summary": "TEST ONLY: Move Robotics Final to C-301",
            "rationale": "Testing human approval flow.",
            "status": "PROPOSED",
            "risk_level": "LOW",
            "estimated_cost": 0,
            "estimated_delay_minutes": 0,
            "actions": [],
        }
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    print("Initial result:")
    print(result)

    print()
    print("Interrupt:")
    print(result["__interrupt__"])

    decision = input(
        "\nApprove this plan? (y/n): "
    ).strip().lower()

    approved = decision == "y"

    result = graph.invoke(
        Command(resume=approved),
        config=config,
    )

    print()
    print("Final result:")
    print(result)


if __name__ == "__main__":
    main()