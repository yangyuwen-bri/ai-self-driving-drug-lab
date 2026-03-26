from __future__ import annotations

from collections.abc import Callable

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, Measurement, PlannerSuggestion
from autoquant.feedback.base import FeedbackProvider


MeasureFn = Callable[[ScenarioSpec, CampaignConfig, PlannerSuggestion, list[Artifact]], Measurement]


class SyntheticFeedbackProvider(FeedbackProvider):
    name = "synthetic"

    def __init__(self, measure_fn: MeasureFn) -> None:
        self._measure_fn = measure_fn

    def collect(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
        artifacts: list[Artifact],
    ) -> Measurement:
        return self._measure_fn(scenario, campaign, suggestion, artifacts)
