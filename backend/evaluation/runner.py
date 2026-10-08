import argparse
import json
import time
from pathlib import Path

from langgraph.types import Command

from backend.agent.graph import build_graph
from evaluation.metrics import calculate_metrics
from evaluation.reset import (
    inject_room_double_booking_failure,
    reset_crowding_fixture,
    reset_room_double_booking_fixture,
)
from evaluation.schemas import EvaluationScenario


SCENARIO_DIR = Path(__file__).parent / "scenarios"
APPROVER_PERSON_ID = 1


def load_scenario(path: Path) -> EvaluationScenario:
    """Load and validate a single evaluation scenario."""
    with path.open() as f:
        data = json.load(f)

    return EvaluationScenario.model_validate(data)


def reset_fixture(scenario: EvaluationScenario) -> None:
    """Reset the database according to the scenario fixture configuration."""
    fixture = scenario.reset_fixture
    fixture_type = fixture.get("type")

    if fixture_type == "room_double_booking":
        reset_room_double_booking_fixture(
            event_id=scenario.event_id,
            source_reservation_id=fixture["source_reservation_id"],
            evaluation_plan_ids=fixture["evaluation_plan_ids"],
        )
        return

    if fixture_type == "crowding":
        reset_crowding_fixture(
            event_id=scenario.event_id,
            source_reservation_id=fixture["source_reservation_id"],
            evaluation_plan_ids=fixture["evaluation_plan_ids"],
        )
        return

    raise ValueError(
        f"Unsupported evaluation fixture type: {fixture_type}"
    )


def inject_failure(scenario: EvaluationScenario) -> None:
    """Inject the failure configured for a recovery scenario."""
    fixture = scenario.reset_fixture
    failure_type = fixture.get("failure_type")

    if failure_type == "cancel_source_reservation":
        inject_room_double_booking_failure(
            source_reservation_id=fixture["source_reservation_id"]
        )
        return

    raise ValueError(
        f"Unsupported failure injection type: {failure_type}"
    )


def run_scenario(
    graph,
    scenario: EvaluationScenario,
) -> dict:
    """Run one scenario through the LangGraph workflow."""
    thread_id = f"evaluation-{scenario.scenario_id}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    initial_state = {
        "user_request": scenario.user_request,
        "event_id": scenario.event_id,
        "approved_by_person_id": APPROVER_PERSON_ID,
    }

    # Phase 1:
    # Run planning, simulation, and approval interrupt.
    first_result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = first_result.get("__interrupt__", [])

    if interrupts:
        approved = scenario.approval_decision == "approve"

        # For recovery scenarios, inject the external failure
        # after planning/simulation but before execution resumes.
        #
        # Only inject it when the human approval decision is APPROVE.
        if (
            approved
            and scenario.expected_outcome.recovery_required
        ):
            inject_failure(scenario)

        # Phase 2:
        # Resume the graph with the human approval decision.
        final_result = graph.invoke(
            Command(resume=approved),
            config=config,
        )
    else:
        final_result = first_result

    return {
        "scenario_id": scenario.scenario_id,
        "approval_decision": scenario.approval_decision,
        "had_approval_interrupt": bool(interrupts),
        "result": final_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run NexCord evaluation scenarios."
    )

    parser.add_argument(
        "scenario",
        nargs="?",
        type=Path,
        help="Path to a single evaluation scenario JSON file.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all evaluation scenarios in the scenarios directory.",
    )

    args = parser.parse_args()

    if args.all and args.scenario:
        parser.error(
            "Do not provide a scenario path together with --all."
        )

    if args.all:
        scenario_paths = sorted(
            SCENARIO_DIR.glob("*.json")
        )

    elif args.scenario:
        scenario_paths = [args.scenario]

    else:
        scenario_paths = [
            SCENARIO_DIR / "room_double_booking_001.json"
        ]

    if not scenario_paths:
        raise ValueError(
            f"No evaluation scenarios found in {SCENARIO_DIR}"
        )

    print("=" * 60)
    print("NexCord Evaluation")
    print("=" * 60)
    print(f"Scenarios: {len(scenario_paths)}")
    print()

    graph = build_graph()

    all_metrics = []

    for scenario_path in scenario_paths:
        scenario = load_scenario(scenario_path)

        print("-" * 60)
        print(f"Scenario: {scenario.name}")
        print(f"ID:       {scenario.scenario_id}")
        print()

        # Put the database into the known initial state.
        reset_fixture(scenario)

        try:
            start_time = time.perf_counter()

            result = run_scenario(
                graph,
                scenario,
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            metrics = calculate_metrics(
                scenario,
                result,
                latency_ms=latency_ms,
            )

            all_metrics.append(metrics)

            print("Evaluation metrics:")
            print(
                json.dumps(
                    metrics,
                    indent=2,
                    default=str,
                )
            )

        finally:
            # Always restore the fixture after the scenario.
            reset_fixture(scenario)

    # ---------------------------------------------------------
    # Aggregate metrics
    # ---------------------------------------------------------

    scenario_pass_rate = (
        sum(
            metric["scenario_passed"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    simulation_success_rate = (
        sum(
            metric["simulation_success"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    approval_handling_rate = (
        sum(
            metric["approval_handled"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    action_selection_accuracy = (
        sum(
            metric["action_selection_correct"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    average_plan_quality = (
        sum(
            metric["plan_quality"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    average_unsafe_action_rate = (
        sum(
            metric["unsafe_action_rate"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    average_latency_ms = (
        sum(
            metric["latency_ms"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    task_completion_rate = (
        sum(
            metric["task_completed"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    execution_success_rate = (
        sum(
            metric["execution_success"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    verification_success_rate = (
        sum(
            metric["verification_success"]
            for metric in all_metrics
        )
        / len(all_metrics)
    )

    recovery_metrics = [
        metric
        for metric in all_metrics
        if metric["recovery_required"]
    ]

    recovery_success_rate = (
        sum(
            metric["recovery_success"]
            for metric in recovery_metrics
        )
        / len(recovery_metrics)
        if recovery_metrics
        else 0.0
    )

    aggregate_metrics = {
        "scenario_count": len(all_metrics),
        "scenario_pass_rate": round(
            scenario_pass_rate,
            4,
        ),
        "simulation_success_rate": round(
            simulation_success_rate,
            4,
        ),
        "approval_handling_rate": round(
            approval_handling_rate,
            4,
        ),
        "action_selection_accuracy": round(
            action_selection_accuracy,
            4,
        ),
        "average_plan_quality": round(
            average_plan_quality,
            4,
        ),
        "average_unsafe_action_rate": round(
            average_unsafe_action_rate,
            4,
        ),
        "task_completion_rate": round(
            task_completion_rate,
            4,
        ),
        "execution_success_rate": round(
            execution_success_rate,
            4,
        ),
        "verification_success_rate": round(
            verification_success_rate,
            4,
        ),
        "recovery_success_rate": round(
            recovery_success_rate,
            4,
        ),
        "average_latency_ms": round(
            average_latency_ms,
            2,
        ),
    }

    print()
    print("=" * 60)
    print("Evaluation Aggregate")
    print("=" * 60)
    print(
        json.dumps(
            aggregate_metrics,
            indent=2,
        )
    )

    print()
    print("=" * 60)
    print("Evaluation Complete")
    print("=" * 60)
    print(
        json.dumps(
            all_metrics,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()