from __future__ import annotations

from autoquant.core.campaigns import CampaignConfig
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Artifact, Measurement, PlannerSuggestion
from autoquant.feedback.base import FeedbackProvider

from .simulator import DrugLabSimulator


class DrugLabFeedbackProvider(FeedbackProvider):
    name = "simulation_feedback"

    def __init__(self, simulator: DrugLabSimulator | None = None) -> None:
        self.simulator = simulator or DrugLabSimulator()

    def collect(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        suggestion: PlannerSuggestion,
        artifacts: list[Artifact],
    ) -> Measurement:
        measurement = self.simulator.run(suggestion.parameters)
        measurement.metadata.update({"artifact_count": len(artifacts)})
        return measurement
