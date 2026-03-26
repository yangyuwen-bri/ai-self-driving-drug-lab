from __future__ import annotations

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, PlannerSuggestion
from autoquant.executors.base import Executor


class DrugLabExecutor(Executor):
    name = "simulation_executor"

    def execute(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
    ) -> list[Artifact]:
        artifact = Artifact(
            artifact_type="execution_payload",
            uri=f"sim://{campaign.campaign_id}/round-{suggestion.metadata.get('round_index', 'pending')}",
            metadata={
                "scenario": scenario.name,
                "campaign_id": campaign.campaign_id,
                "parameters": suggestion.parameters,
                "planner": suggestion.planner_name,
            },
        )
        return [artifact]
