from __future__ import annotations

from abc import ABC, abstractmethod

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, PlannerSuggestion


class Executor(ABC):
    name: str

    @abstractmethod
    def execute(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
    ) -> list[Artifact]:
        raise NotImplementedError

