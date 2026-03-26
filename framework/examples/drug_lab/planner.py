from __future__ import annotations

import random

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import PlannerSuggestion
from autoquant.planners.base import Planner

from .common import compute_desirability, sample_parameters


class DrugLabPlanner(Planner):
    name = "simulation_heuristic_planner"

    def __init__(self, seed: int = 11, bootstrap_rounds: int = 3, candidates_per_round: int = 192) -> None:
        self.rng = random.Random(seed)
        self.bootstrap_rounds = bootstrap_rounds
        self.candidates_per_round = candidates_per_round

    def propose(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        history: list[CampaignRoundRecord],
    ) -> PlannerSuggestion:
        if len(history) < self.bootstrap_rounds:
            parameters = sample_parameters(scenario, self.rng)
            return PlannerSuggestion(
                planner_name=self.name,
                parameters=parameters,
                rationale="bootstrap random exploration",
                metadata={"phase": "bootstrap"},
            )

        target_half_life = campaign.target["half_life"]
        best_candidate = None
        best_score = float("-inf")
        for _ in range(self.candidates_per_round):
            candidate = sample_parameters(scenario, self.rng)
            proxy_values = self._proxy_predict(candidate)
            desirability = compute_desirability(proxy_values, campaign.target, scenario.objectives)
            target_error = abs(proxy_values["half_life"] - target_half_life)
            exploration = self._distance_bonus(candidate, history)
            final_score = desirability * 0.7 + exploration * 0.2 - target_error * 0.1
            if final_score > best_score:
                best_candidate = candidate
                best_score = final_score

        assert best_candidate is not None
        return PlannerSuggestion(
            planner_name=self.name,
            parameters=best_candidate,
            score=best_score,
            rationale="heuristic desirability search over sampled candidates",
            metadata={"phase": "guided_search", "candidates": self.candidates_per_round},
        )

    @staticmethod
    def _distance_bonus(candidate: dict[str, float], history: list[CampaignRoundRecord]) -> float:
        if not history:
            return 1.0
        best = None
        for record in history:
            diff = 0.0
            for key, value in candidate.items():
                diff += abs(value - record.parameters[key])
            best = diff if best is None else min(best, diff)
        return min(best / 600.0, 1.0) if best is not None else 1.0

    @staticmethod
    def _proxy_predict(candidate: dict[str, float]) -> dict[str, float]:
        t = candidate["temperature"]
        h = candidate["humidity"]
        aux1 = candidate["aux1_ratio"]
        aux2 = candidate["aux2_ratio"]
        duration = candidate["duration"]
        speed = candidate["stirring_speed"]
        ph = candidate["pH"]
        solvent = candidate["solvent_concentration"]
        return {
            "half_life": (
                17.2
                - 0.010 * (t - 42.0) ** 2
                - 0.003 * (h - 58.0) ** 2
                - 0.30 * (ph - 6.2) ** 2
                + 0.48 * aux2
                + 0.12 * aux1
                + 0.010 * duration
                - 0.004 * solvent
            ),
            "stability_index": 90.0 - 0.018 * (t - 36.0) ** 2 - 1.4 * abs(ph - 6.0) + 1.6 * aux2,
            "solubility": 5.0 + 0.35 * solvent + 1.4 * aux1 - 0.05 * aux2,
        }
