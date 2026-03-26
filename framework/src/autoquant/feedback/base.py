from __future__ import annotations

from abc import ABC, abstractmethod

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, Measurement, PlannerSuggestion


class FeedbackProvider(ABC):
    name: str

    @abstractmethod
    def collect(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
        artifacts: list[Artifact],
    ) -> Measurement:
        raise NotImplementedError

