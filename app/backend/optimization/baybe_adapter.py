from __future__ import annotations

from typing import Sequence

import pandas as pd

from app.backend.core.config import PARAMETER_BOUNDS
from app.backend.models.schemas import ExperimentParameters, ExperimentRecord, ObjectiveWeights
from app.backend.optimization.surrogate_optimizer import OptimizerRecommendation, SurrogateOptimizer


class BayBEOptimizerAdapter:
    """Uses BayBE as the primary optimizer and fails fast on BayBE errors."""

    def __init__(self) -> None:
        self._surrogate = SurrogateOptimizer()
        self._baybe_available = self._check_baybe()

    @staticmethod
    def _check_baybe() -> bool:
        try:
            import baybe  # noqa: F401
        except Exception:
            return False
        return True

    def suggest(
        self,
        history: Sequence[ExperimentRecord],
        desired_half_life: float,
        tolerance: float,
        weights: ObjectiveWeights,
        target_mode: str,
        initial_random_samples: int,
        strategy: str,
    ) -> OptimizerRecommendation:
        if strategy == "surrogate":
            return self._surrogate.suggest(
                history=history,
                desired_half_life=desired_half_life,
                tolerance=tolerance,
                weights=weights,
                target_mode=target_mode,
                initial_random_samples=initial_random_samples,
            )

        if strategy != "baybe":
            raise ValueError(
                f"Unsupported optimization strategy '{strategy}'. "
                "Use 'baybe' for production runs or 'surrogate' for explicit benchmarking."
            )

        return self._suggest_baybe(
            history=history,
            desired_half_life=desired_half_life,
            tolerance=tolerance,
            weights=weights,
            target_mode=target_mode,
            initial_random_samples=initial_random_samples,
        )

    def _suggest_baybe(
        self,
        history: Sequence[ExperimentRecord],
        desired_half_life: float,
        tolerance: float,
        weights: ObjectiveWeights,
        target_mode: str,
        initial_random_samples: int,
    ) -> OptimizerRecommendation:
        if not self._baybe_available:
            raise RuntimeError(
                "BayBE is not installed in this environment. "
                "Install requirements.txt before running BayBE experiments."
            )

        try:
            from baybe import Campaign
            from baybe.objectives import DesirabilityObjective, SingleTargetObjective
            from baybe.objectives.desirability import Scalarizer
            from baybe.parameters import NumericalContinuousParameter
            from baybe.recommenders import BotorchRecommender, RandomRecommender, TwoPhaseMetaRecommender
            from baybe.searchspace import SearchSpace
            from baybe.targets import NumericalTarget
        except Exception as exc:
            raise RuntimeError("BayBE is installed but could not be imported cleanly.") from exc

        try:
            parameters = [
                NumericalContinuousParameter(name=name, bounds=(lower, upper))
                for name, (lower, upper) in PARAMETER_BOUNDS.items()
            ]
            searchspace = SearchSpace.from_product(parameters=parameters)

            if target_mode == "single":
                target = NumericalTarget.match_bell(
                    name="half_life",
                    match_value=desired_half_life,
                    sigma=max(tolerance, 0.1),
                )
                objective = SingleTargetObjective(target=target)
            else:
                targets = [
                    NumericalTarget.match_bell(
                        name="half_life",
                        match_value=desired_half_life,
                        sigma=max(tolerance, 0.1),
                    ),
                    NumericalTarget.normalized_ramp(name="stability_index", cutoffs=(40.0, 100.0)),
                    NumericalTarget.normalized_ramp(name="solubility", cutoffs=(2.0, 35.0)),
                ]
                objective = DesirabilityObjective(
                    targets=targets,
                    weights=[weights.half_life, weights.stability_index, weights.solubility],
                    scalarizer=Scalarizer.MEAN,
                )

            recommender = TwoPhaseMetaRecommender(
                initial_recommender=RandomRecommender(),
                recommender=BotorchRecommender(),
                switch_after=initial_random_samples,
                remain_switched=True,
            )
            campaign = Campaign(searchspace=searchspace, objective=objective, recommender=recommender)

            if history:
                records = []
                for record in history:
                    row = record.parameters.as_dict() | {
                        "half_life": record.result.half_life,
                        "stability_index": record.result.stability_index,
                        "solubility": record.result.solubility,
                    }
                    records.append(row)
                campaign.add_measurements(pd.DataFrame(records))

            rec_df = campaign.recommend(batch_size=1)
            row = rec_df.iloc[0].to_dict()
            params = ExperimentParameters(**{key: float(row[key]) for key in PARAMETER_BOUNDS})
            strategy_name = "baybe_random" if len(history) < initial_random_samples else "baybe_botorch"
            return OptimizerRecommendation(parameters=params, strategy=strategy_name)
        except Exception as exc:
            raise RuntimeError("BayBE optimization failed and no surrogate fallback is allowed.") from exc
