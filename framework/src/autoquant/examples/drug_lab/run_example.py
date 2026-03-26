from __future__ import annotations

import argparse
import json
from uuid import uuid4

from autoquant.core import CampaignConfig
from autoquant.modeling import InMemoryModelRegistry
from autoquant.orchestration import SequentialOrchestrator
from autoquant.planners import AdaptivePlanner, RandomPlanner
from autoquant.storage import InMemoryCampaignStore

from .executor import DrugLabExecutor
from .feedback import DrugLabFeedbackProvider
from .planner import DrugLabPlanner
from .spec import DRUG_LAB_SCENARIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AutoQuant drug-lab simulation example.")
    parser.add_argument("--target-half-life", type=float, default=12.0, help="Desired half_life in hours.")
    parser.add_argument("--tolerance", type=float, default=0.5, help="Stopping tolerance on half_life error.")
    parser.add_argument("--max-rounds", type=int, default=8, help="Maximum rounds for the campaign.")
    parser.add_argument("--campaign-id", type=str, default="", help="Optional campaign id.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    campaign = CampaignConfig(
        campaign_id=args.campaign_id or f"drug-lab-{uuid4().hex[:8]}",
        scenario_name=DRUG_LAB_SCENARIO.name,
        target={"half_life": args.target_half_life},
        tolerance=args.tolerance,
        max_rounds=args.max_rounds,
        strategy="simulation_first",
        metadata={"example": "drug_lab"},
    )

    store = InMemoryCampaignStore()
    registry = InMemoryModelRegistry()
    planner = AdaptivePlanner(
        planners={
            "simulation_heuristic_planner": DrugLabPlanner(),
            "random": RandomPlanner(seed=17),
        },
        model_registry=registry,
        warmup_rounds_per_planner=1,
    )
    orchestrator = SequentialOrchestrator(
        planner=planner,
        executor=DrugLabExecutor(),
        feedback_provider=DrugLabFeedbackProvider(),
        store=store,
        model_registry=registry,
    )

    history = orchestrator.run_campaign(DRUG_LAB_SCENARIO, campaign)
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
        "result": {
            "status": campaign.status.value,
            "best_round": best_round.round_index if best_round else None,
            "best_parameters": best_round.parameters if best_round else None,
            "best_measurement": best_round.measurement.values if best_round and best_round.measurement else None,
            "best_metadata": {
                "target_error": best_round.target_error,
                "objective_score": best_round.measurement.objective_score if best_round and best_round.measurement else None,
            }
            if best_round
            else None,
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
                "parameters": record.parameters,
                "measurement": record.measurement.values if record.measurement else None,
                "target_error": record.target_error,
                "objective_score": record.measurement.objective_score if record.measurement else None,
                "metadata": record.measurement.metadata if record.measurement else {},
            }
            for record in history
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
