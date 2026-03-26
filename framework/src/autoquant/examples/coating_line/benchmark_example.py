from __future__ import annotations

import argparse
import json

from autoquant.benchmarking import benchmark_planners
from autoquant.core import CampaignConfig, Measurement
from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.planners import BayBEPlanner, RandomPlanner, baybe_available

from .simulator import CoatingLineSimulator
from .spec import COATING_LINE_SCENARIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark planners on the coating-line scenario.")
    parser.add_argument("--target-thickness", type=float, default=85.0, help="Desired coating thickness.")
    parser.add_argument("--tolerance", type=float, default=3.0, help="Stopping tolerance on thickness error.")
    parser.add_argument("--max-rounds", type=int, default=5, help="Maximum rounds per campaign.")
    parser.add_argument("--replicates", type=int, default=3, help="How many benchmark campaigns per planner.")
    return parser.parse_args()


def _feedback_factory():
    simulator = CoatingLineSimulator()

    def measure(scenario, campaign, suggestion, artifacts) -> Measurement:
        measurement = simulator.run(suggestion.parameters)
        measurement.metadata["artifact_count"] = len(artifacts)
        return measurement

    return SyntheticFeedbackProvider(measure)


def main() -> int:
    args = parse_args()
    planner_factories = {"random": lambda: RandomPlanner(seed=29)}
    if baybe_available():
        planner_factories["baybe"] = lambda: BayBEPlanner(initial_random_samples=2)

    report = benchmark_planners(
        scenario=COATING_LINE_SCENARIO,
        campaign_template=CampaignConfig(
            campaign_id="coating-benchmark",
            scenario_name=COATING_LINE_SCENARIO.name,
            target={"coating_thickness": args.target_thickness},
            tolerance=args.tolerance,
            max_rounds=args.max_rounds,
            strategy="benchmark",
            metadata={"example": "coating_line"},
        ),
        planner_factories=planner_factories,
        executor_factory=NoOpExecutor,
        feedback_factory=_feedback_factory,
        replicates=args.replicates,
    )
    payload = {
        "scenario": report.scenario_name,
        "target": report.target,
        "tolerance": report.tolerance,
        "replicates": report.replicates,
        "summaries": [
            {
                "planner_name": item.planner_name,
                "trials_count": item.trials_count,
                "success_rate": round(item.success_rate, 4),
                "avg_best_error": round(item.avg_best_error, 4),
                "avg_rounds_run": round(item.avg_rounds_run, 4),
                "avg_best_objective_score": (
                    round(item.avg_best_objective_score, 4)
                    if item.avg_best_objective_score is not None
                    else None
                ),
            }
            for item in report.summaries
        ],
        "trials": [
            {
                "planner_name": item.planner_name,
                "replicate_index": item.replicate_index,
                "campaign_id": item.campaign_id,
                "status": item.status,
                "rounds_run": item.rounds_run,
                "best_round_index": item.best_round_index,
                "best_error": item.best_error,
                "best_objective_score": item.best_objective_score,
            }
            for item in report.trials
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
