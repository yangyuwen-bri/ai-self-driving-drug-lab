from __future__ import annotations

import random

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import PlannerSuggestion
from autoquant.planners.base import Planner


class RandomPlanner(Planner):
    name = "random"

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def propose(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        history: list[CampaignRoundRecord],
    ) -> PlannerSuggestion:
        parameters = {
            spec.name: self._rng.uniform(spec.lower, spec.upper)
            for spec in scenario.parameters
        }
        return PlannerSuggestion(
            planner_name=self.name,
            parameters=parameters,
            rationale=f"uniform random sample from {len(scenario.parameters)} parameter bounds",
            metadata={
                "history_size": len(history),
                "strategy": campaign.strategy,
            },
        )
