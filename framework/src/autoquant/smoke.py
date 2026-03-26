from __future__ import annotations

import json
from pprint import pprint

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ObjectiveSpec, ParameterSpec, ScenarioSpec
from autoquant.core.types import Measurement
from autoquant.executors.noop import NoOpExecutor
from autoquant.feedback.synthetic import SyntheticFeedbackProvider
from autoquant.orchestration.sequential import SequentialOrchestrator
from autoquant.planners.random import RandomPlanner
from autoquant.storage.memory import InMemoryCampaignStore


def _synthetic_measurement(
    scenario: ScenarioSpec,
    campaign: CampaignConfig,
    suggestion,
    artifacts,
) -> Measurement:
    params = suggestion.parameters
    half_life = (
        18.0
        - 0.02 * (params["temperature"] - 42.0) ** 2
        - 0.01 * (params["humidity"] - 58.0) ** 2
        + 0.4 * params["aux1_ratio"]
    )
    return Measurement(
        values={
            "half_life": half_life,
            "solubility": 5.0 + 0.2 * params["aux1_ratio"],
        },
        source="synthetic",
        metadata={"artifacts_seen": len(artifacts), "scenario": scenario.name},
    )


def build_demo_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        name="formulation_demo",
        parameters=[
            ParameterSpec("temperature", 20.0, 80.0, unit="°C"),
            ParameterSpec("humidity", 40.0, 80.0, unit="%"),
            ParameterSpec("aux1_ratio", 0.5, 5.0, unit="%"),
        ],
        objectives=[
            ObjectiveSpec("half_life", mode="match_bell", target=12.0, tolerance=0.5, unit="h"),
        ],
        fixed_components={"primary_api_ratio": 20.0},
    )


def run_smoke_campaign() -> dict:
    scenario = build_demo_scenario()
    campaign = CampaignConfig(
        campaign_id="smoke-campaign",
        scenario_name=scenario.name,
        target={"half_life": 12.0},
        tolerance=0.5,
        max_rounds=5,
        strategy="random",
    )
    store = InMemoryCampaignStore()
    orchestrator = SequentialOrchestrator(
        planner=RandomPlanner(seed=7),
        executor=NoOpExecutor(),
        feedback_provider=SyntheticFeedbackProvider(_synthetic_measurement),
        store=store,
    )
    rounds = orchestrator.run_campaign(scenario, campaign)
    final_campaign = store.get_campaign(campaign.campaign_id)
    return {
        "campaign": {
            "campaign_id": final_campaign.campaign_id if final_campaign else campaign.campaign_id,
            "status": final_campaign.status if final_campaign else "unknown",
            "current_round": final_campaign.current_round if final_campaign else len(rounds),
        },
        "rounds": [
            {
                "round_index": record.round_index,
                "status": str(record.status),
                "planner_name": record.planner_name,
                "target_error": record.target_error,
                "measurement": record.measurement.values if record.measurement else None,
            }
            for record in rounds
        ],
    }


def main() -> None:
    result = run_smoke_campaign()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("\nsummary:")
    pprint(result["campaign"])


if __name__ == "__main__":
    main()
