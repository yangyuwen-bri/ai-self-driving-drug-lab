from __future__ import annotations

from typing import Sequence

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ObjectiveSpec, ScenarioSpec
from autoquant.core.types import PlannerSuggestion
from autoquant.planners.base import Planner


def baybe_available() -> bool:
    try:
        import baybe  # noqa: F401
    except Exception:
        return False
    return True


class BayBEPlanner(Planner):
    """BayBE-backed planner plugin for target-driven continuous optimization."""

    name = "baybe"

    def __init__(
        self,
        *,
        initial_random_samples: int = 3,
    ) -> None:
        self.initial_random_samples = max(initial_random_samples, 1)
        self._available = baybe_available()

    def propose(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
        history: list[CampaignRoundRecord],
    ) -> PlannerSuggestion:
        if not self._available:
            raise RuntimeError("BayBE is not installed in this environment.")

        from baybe import Campaign
        from baybe.objectives import DesirabilityObjective, SingleTargetObjective
        from baybe.objectives.desirability import Scalarizer
        from baybe.parameters import NumericalContinuousParameter
        from baybe.recommenders import BotorchRecommender, RandomRecommender, TwoPhaseMetaRecommender
        from baybe.searchspace import SearchSpace

        parameters = [
            NumericalContinuousParameter(
                name=parameter.name,
                bounds=(parameter.lower, parameter.upper),
            )
            for parameter in scenario.parameters
        ]
        searchspace = SearchSpace.from_product(parameters=parameters)
        objective = self._build_objective(scenario, campaign)
        recommender = TwoPhaseMetaRecommender(
            initial_recommender=RandomRecommender(),
            recommender=BotorchRecommender(),
            switch_after=self.initial_random_samples,
            remain_switched=True,
        )
        baybe_campaign = Campaign(
            searchspace=searchspace,
            objective=objective,
            recommender=recommender,
        )

        measurements_df = self._history_to_measurements(history, scenario)
        if not measurements_df.empty:
            baybe_campaign.add_measurements(measurements_df)

        recommendation_df = baybe_campaign.recommend(batch_size=1)
        recommendation = recommendation_df.iloc[0]
        params = {
            parameter.name: float(recommendation[parameter.name])
            for parameter in scenario.parameters
        }
        phase = "baybe_random" if len(history) < self.initial_random_samples else "baybe_botorch"
        return PlannerSuggestion(
            planner_name=self.name,
            parameters=params,
            rationale=f"recommended by BayBE ({phase})",
            metadata={
                "selected_by": self.name,
                "phase": phase,
                "history_size": len(history),
            },
        )

    def _build_objective(self, scenario: ScenarioSpec, campaign: CampaignConfig):
        from baybe.objectives import DesirabilityObjective, SingleTargetObjective
        from baybe.objectives.desirability import Scalarizer
        from baybe.targets import NumericalTarget

        if len(scenario.objectives) == 1:
            objective = scenario.objectives[0]
            return SingleTargetObjective(
                target=self._build_target(objective, campaign),
            )

        return DesirabilityObjective(
            targets=[self._build_target(objective, campaign) for objective in scenario.objectives],
            weights=[objective.weight for objective in scenario.objectives],
            scalarizer=Scalarizer.MEAN,
        )

    def _build_target(self, objective: ObjectiveSpec, campaign: CampaignConfig):
        from baybe.targets import NumericalTarget

        if objective.mode == "match_bell":
            target_value = campaign.target.get(objective.name, objective.target)
            if target_value is None:
                raise ValueError(f"Objective '{objective.name}' requires a target value.")
            return NumericalTarget.match_bell(
                name=objective.name,
                match_value=float(target_value),
                sigma=float(objective.tolerance or campaign.tolerance),
            )

        if objective.mode == "maximize":
            lower = float(objective.metadata.get("lower_bound", 0.0))
            upper = float(objective.metadata.get("upper_bound", 1.0))
            return NumericalTarget.normalized_ramp(
                name=objective.name,
                cutoffs=(lower, upper),
            )

        raise ValueError(f"Unsupported objective mode for BayBEPlanner: {objective.mode}")

    @staticmethod
    def _history_to_measurements(
        history: Sequence[CampaignRoundRecord],
        scenario: ScenarioSpec,
    ):
        import pandas as pd

        rows: list[dict[str, float]] = []
        objective_names = [objective.name for objective in scenario.objectives]
        for record in history:
            if record.measurement is None:
                continue
            row = {key: float(value) for key, value in record.parameters.items()}
            missing_objective = False
            for objective_name in objective_names:
                value = record.measurement.values.get(objective_name)
                if value is None:
                    missing_objective = True
                    break
                row[objective_name] = float(value)
            if not missing_objective:
                rows.append(row)
        return pd.DataFrame(rows)
