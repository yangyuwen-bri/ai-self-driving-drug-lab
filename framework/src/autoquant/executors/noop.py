from __future__ import annotations

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, PlannerSuggestion
from autoquant.executors.base import Executor


class NoOpExecutor(Executor):
    name = "noop"

    def execute(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
    ) -> list[Artifact]:
        return [
            Artifact(
                artifact_type="execution_payload",
                uri=f"memory://{campaign.campaign_id}/{suggestion.planner_name}",
                metadata={
                    "scenario": scenario.name,
                    "parameters": suggestion.parameters,
                },
            )
        ]
