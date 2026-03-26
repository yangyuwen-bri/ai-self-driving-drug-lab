from __future__ import annotations

from collections import Counter

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import PlannerSuggestion
from autoquant.modeling.base import ModelRegistry
from autoquant.planners.base import Planner


class AdaptivePlanner(Planner):
    """Wrap multiple planners and choose among them using warmup + score history."""

    name = "adaptive"

    def __init__(
        self,
        planners: dict[str, Planner],
        model_registry: ModelRegistry | None = None,
        warmup_rounds_per_planner: int = 1,
    ) -> None:
        if not planners:
            raise ValueError("AdaptivePlanner requires at least one planner.")
        self._planners = planners
        self._registry = model_registry
        self._warmup_rounds_per_planner = max(warmup_rounds_per_planner, 1)

    def propose(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        history: list[CampaignRoundRecord],
    ) -> PlannerSuggestion:
        planner_name, reason = self._select_planner(history)
        planner = self._planners[planner_name]
        suggestion = planner.propose(scenario, campaign, history)
        suggestion.metadata.update(
            {
                "selected_by": self.name,
                "selected_planner": planner_name,
                "selection_reason": reason,
            }
        )
        suggestion.rationale = f"{reason}; {suggestion.rationale}".strip("; ")
        return suggestion

    def _select_planner(self, history: list[CampaignRoundRecord]) -> tuple[str, str]:
        planner_counts = Counter(record.planner_name for record in history if record.planner_name)
        for planner_name in self._planners:
            if planner_counts.get(planner_name, 0) < self._warmup_rounds_per_planner:
                return planner_name, "warmup exploration"

        if self._registry is None:
            planner_name = next(iter(self._planners))
            return planner_name, "defaulted to first planner"

        score_map = {score.planner_name: score for score in self._registry.summarize()}
        ranked = [
            (name, score_map.get(name))
            for name in self._planners
        ]
        ranked.sort(
            key=lambda item: (
                item[1].avg_error if item[1] is not None else float("inf"),
                -(item[1].success_rate if item[1] is not None else 0.0),
                -(item[1].runs_count if item[1] is not None else 0),
            )
        )
        chosen = ranked[0][0]
        return chosen, "selected by historical planner score"
