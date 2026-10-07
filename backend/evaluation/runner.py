import json
from pathlib import Path

from langgraph.types import Command

from backend.agent.graph import build_graph
from evaluation.schemas import EvaluationScenario
from evaluation.metrics import calculate_metrics
from evaluation.reset import reset_room_double_booking_fixture
import time


SCENARIO_DIR = Path(__file__).parent / "scenarios"
APPROVER_PERSON_ID = 1


def load_scenario(path: Path) -> EvaluationScenario:
    with path.open() as f:
        data = json.load(f)

    return EvaluationScenario.model_validate(data)


def run_scenario(graph, scenario: EvaluationScenario) -> dict:
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

    first_result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = first_result.get("__interrupt__", [])

    if interrupts:
        approved = scenario.approval_decision == "approve"

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

def reset_scenario(scenario: EvaluationScenario) -> None:
    fixture = scenario.reset_fixture

    fixture_type = fixture.get("type")

    if fixture_type == "room_double_booking":
        reset_room_double_booking_fixture(
            event_id=scenario.event_id,
            source_reservation_id=fixture["source_reservation_id"],
            evaluation_plan_ids=fixture["evaluation_plan_ids"],
        )
        return

    raise ValueError(
        f"Unsupported reset fixture type: {fixture_type}"
    )

def main() -> None:
    import argparse

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

        reset_scenario(scenario)

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
            reset_scenario(scenario)

    scenario_pass_rate = (
        sum(metric["scenario_passed"] for metric in all_metrics)
        / len(all_metrics)
    )

    simulation_success_rate = (
        sum(metric["simulation_success"] for metric in all_metrics)
        / len(all_metrics)
    )

    approval_handling_rate = (
        sum(metric["approval_handled"] for metric in all_metrics)
        / len(all_metrics)
    )

    action_selection_accuracy = (
        sum(metric["action_selection_correct"] for metric in all_metrics)
        / len(all_metrics)
    )

    average_plan_quality = (
        sum(metric["plan_quality"] for metric in all_metrics)
        / len(all_metrics)
    )

    average_unsafe_action_rate = (
        sum(metric["unsafe_action_rate"] for metric in all_metrics)
        / len(all_metrics)
    )

    average_latency_ms = (
        sum(metric["latency_ms"] for metric in all_metrics)
        / len(all_metrics)
    )

    aggregate_metrics = {
        "scenario_count": len(all_metrics),
        "scenario_pass_rate": round(scenario_pass_rate, 4),
        "simulation_success_rate": round(simulation_success_rate, 4),
        "approval_handling_rate": round(approval_handling_rate, 4),
        "action_selection_accuracy": round(action_selection_accuracy, 4),
        "average_plan_quality": round(average_plan_quality, 4),
        "average_unsafe_action_rate": round(average_unsafe_action_rate, 4),
        "average_latency_ms": round(average_latency_ms, 2),
    }

    print()
    print("=" * 60)
    print("Evaluation Aggregate")
    print("=" * 60)
    print(json.dumps(aggregate_metrics, indent=2))

    print()
    print("=" * 60)
    print("Evaluation Complete")
    print("=" * 60)
    print(json.dumps(all_metrics, indent=2, default=str))

if __name__ == "__main__":
    main()