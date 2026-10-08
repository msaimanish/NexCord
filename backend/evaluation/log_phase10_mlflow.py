import json
import re
from pathlib import Path

import mlflow


RESULTS_FILE = Path("evaluation/results_phase10.txt")
EXPERIMENT_NAME = "NexCord Phase 10 Evaluation"


def load_aggregate_metrics() -> dict:
    text = RESULTS_FILE.read_text()

    match = re.search(
        r"Evaluation Aggregate\s*"
        r"=+\s*"
        r"(\{.*?\})\s*"
        r"\n\s*={3,}",
        text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError(
            "Could not find Evaluation Aggregate in results file."
        )

    return json.loads(match.group(1))


def main() -> None:
    metrics = load_aggregate_metrics()

    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(
        run_name="phase10_54_scenario_benchmark"
    ):
        mlflow.log_params(
            {
                "scenario_count": metrics["scenario_count"],
                "benchmark_type": "simulated_incident_evaluation",
                "evaluation_mode": "NEXCORD_EVAL_MODE",
                "llm_reasoning": "skipped_for_benchmark_stability",
            }
        )

        mlflow.log_metrics(
            {
                "scenario_pass_rate": metrics["scenario_pass_rate"],
                "simulation_success_rate": metrics[
                    "simulation_success_rate"
                ],
                "approval_handling_rate": metrics[
                    "approval_handling_rate"
                ],
                "action_selection_accuracy": metrics[
                    "action_selection_accuracy"
                ],
                "average_plan_quality": metrics[
                    "average_plan_quality"
                ],
                "average_unsafe_action_rate": metrics[
                    "average_unsafe_action_rate"
                ],
                "task_completion_rate": metrics[
                    "task_completion_rate"
                ],
                "execution_success_rate": metrics[
                    "execution_success_rate"
                ],
                "verification_success_rate": metrics[
                    "verification_success_rate"
                ],
                "recovery_success_rate": metrics[
                    "recovery_success_rate"
                ],
                "average_latency_ms": metrics[
                    "average_latency_ms"
                ],
            }
        )

        mlflow.log_artifact(RESULTS_FILE)

        report_file = Path(
            "evaluation/phase10_evaluation_report.md"
        )

        if report_file.exists():
            mlflow.log_artifact(report_file)

        run = mlflow.active_run()

        print("MLflow logging complete")
        print("Experiment:", EXPERIMENT_NAME)
        print("Run ID:", run.info.run_id)
        print("Tracking:", mlflow.get_tracking_uri())


if __name__ == "__main__":
    main()
