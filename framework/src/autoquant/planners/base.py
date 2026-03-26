from __future__ import annotations

from abc import ABC, abstractmethod

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import PlannerSuggestion


class Planner(ABC):
    name: str

    @abstractmethod
    def propose(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        history: list[CampaignRoundRecord],
    ) -> PlannerSuggestion:
        raise NotImplementedError

