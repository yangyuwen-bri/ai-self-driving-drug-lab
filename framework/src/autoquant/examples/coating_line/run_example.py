from __future__ import annotations

import argparse
import json
from uuid import uuid4

from autoquant.core import CampaignConfig, Measurement
from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.modeling import InMemoryModelRegistry
from autoquant.orchestration import SequentialOrchestrator
from autoquant.planners import AdaptivePlanner, BayBEPlanner, RandomPlanner, baybe_available
from autoquant.storage import InMemoryCampaignStore

from .simulator import CoatingLineSimulator
from .spec import COATING_LINE_SCENARIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AutoQuant coating-line example.")
    parser.add_argument("--target-thickness", type=float, default=85.0, help="Desired coating thickness in microns.")
    parser.add_argument("--tolerance", type=float, default=3.0, help="Stopping tolerance on thickness error.")
    parser.add_argument("--max-rounds", type=int, default=8, help="Maximum rounds for the campaign.")
    return parser.parse_args()


def _build_measure_fn(simulator: CoatingLineSimulator):
    def measure(scenario, campaign, suggestion, artifacts) -> Measurement:
        measurement = simulator.run(suggestion.parameters)
        measurement.metadata["artifact_count"] = len(artifacts)
        return measurement

    return measure


def _build_planner(registry: InMemoryModelRegistry) -> AdaptivePlanner:
    planners = {"random": RandomPlanner(seed=29)}
    if baybe_available():
        planners["baybe"] = BayBEPlanner(initial_random_samples=2)
    return AdaptivePlanner(
        planners=planners,
        model_registry=registry,
        warmup_rounds_per_planner=1,
    )


def main() -> int:
    args = parse_args()
    campaign = CampaignConfig(
        campaign_id=f"coating-line-{uuid4().hex[:8]}",
        scenario_name=COATING_LINE_SCENARIO.name,
        target={"coating_thickness": args.target_thickness},
        tolerance=args.tolerance,
        max_rounds=args.max_rounds,
        strategy="simulation_first",
        metadata={"example": "coating_line"},
    )
    store = InMemoryCampaignStore()
    registry = InMemoryModelRegistry()
    simulator = CoatingLineSimulator()
    orchestrator = SequentialOrchestrator(
        planner=_build_planner(registry),
        executor=NoOpExecutor(),
        feedback_provider=SyntheticFeedbackProvider(_build_measure_fn(simulator)),
        store=store,
        model_registry=registry,
    )
    history = orchestrator.run_campaign(COATING_LINE_SCENARIO, campaign)
    best_round = (
        min(history, key=lambda record: record.target_error if record.target_error is not None else float("inf"))
        if history
        else None
    )
    payload = {
        "campaign": {
            "campaign_id": campaign.campaign_id,
            "target": campaign.target,
            "tolerance": campaign.tolerance,
            "max_rounds": campaign.max_rounds,
            "status": campaign.status.value,
        },
        "best_round": {
            "round_index": best_round.round_index if best_round else None,
            "planner_name": best_round.planner_name if best_round else None,
            "parameters": best_round.parameters if best_round else None,
            "measurement": best_round.measurement.values if best_round and best_round.measurement else None,
            "target_error": best_round.target_error if best_round else None,
            "objective_score": best_round.measurement.objective_score if best_round and best_round.measurement else None,
        },
        "planner_scores": [
            {
                "planner_name": score.planner_name,
                "avg_error": round(score.avg_error, 4),
                "success_rate": round(score.success_rate, 4),
                "runs_count": score.runs_count,
            }
            for score in registry.summarize()
        ],
        "rounds": [
            {
                "round_index": record.round_index,
                "planner_name": record.planner_name,
                "target_error": record.target_error,
                "measurement": record.measurement.values if record.measurement else None,
            }
            for record in history
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
