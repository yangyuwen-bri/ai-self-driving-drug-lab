from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from app.backend.core.config import PARAMETER_BOUNDS
from app.backend.models.schemas import ExperimentParameters, ExperimentRecord, ObjectiveWeights
from app.backend.optimization.objectives import compute_desirability


@dataclass
class OptimizerRecommendation:
    parameters: ExperimentParameters
    strategy: str


class SurrogateOptimizer:
    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def suggest(
        self,
        history: Sequence[ExperimentRecord],
        desired_half_life: float,
        tolerance: float,
        weights: ObjectiveWeights,
        target_mode: str,
        initial_random_samples: int,
    ) -> OptimizerRecommendation:
        if len(history) < initial_random_samples:
            return OptimizerRecommendation(parameters=self._sample_random(), strategy="random_bootstrap")

        x_train = np.array([record.parameters.as_feature_vector() for record in history])
        y_train = np.array([record.result.desirability for record in history])

        model = RandomForestRegressor(
            n_estimators=220,
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
        )
        model.fit(x_train, y_train)

        candidates = [self._sample_random() for _ in range(256)]
        scores: List[tuple[float, ExperimentParameters]] = []
        for candidate in candidates:
            features = np.array(candidate.as_feature_vector()).reshape(1, -1)
            predicted = float(model.predict(features)[0])
            exploration_bonus = self._distance_bonus(candidate, history)
            desirability_hint = self._physics_prior(candidate, desired_half_life, tolerance, weights, target_mode)
            final_score = 0.60 * predicted + 0.25 * exploration_bonus + 0.15 * desirability_hint
            scores.append((final_score, candidate))

        best = max(scores, key=lambda item: item[0])[1]
        return OptimizerRecommendation(parameters=best, strategy="surrogate_random_forest")

    def _sample_random(self) -> ExperimentParameters:
        values = {
            name: round(self.rng.uniform(lower, upper), 4)
            for name, (lower, upper) in PARAMETER_BOUNDS.items()
        }
        return ExperimentParameters(**values)

    @staticmethod
    def _distance_bonus(candidate: ExperimentParameters, history: Sequence[ExperimentRecord]) -> float:
        if not history:
            return 1.0
        candidate_vector = np.array(candidate.as_feature_vector(), dtype=float)
        distances = []
        for record in history:
            vector = np.array(record.parameters.as_feature_vector(), dtype=float)
            distances.append(float(np.linalg.norm(candidate_vector - vector)))
        return float(np.tanh(min(distances) / 100.0))

    @staticmethod
    def _physics_prior(
        candidate: ExperimentParameters,
        desired_half_life: float,
        tolerance: float,
        weights: ObjectiveWeights,
        target_mode: str,
    ) -> float:
        heuristic_half_life = (
            16.0
            - 0.01 * (candidate.temperature - 42.0) ** 2
            - 0.002 * (candidate.humidity - 58.0) ** 2
            - 0.35 * (candidate.pH - 6.2) ** 2
            + 0.45 * candidate.aux2_ratio
            + 0.1 * candidate.aux1_ratio
        )
        heuristic_result = type("HeuristicResult", (), {})()
        heuristic_result.half_life = heuristic_half_life
        heuristic_result.stability_index = 85.0 - 0.02 * (candidate.temperature - 36.0) ** 2
        heuristic_result.solubility = 5.0 + 0.35 * candidate.solvent_concentration + 1.5 * candidate.aux1_ratio
        desirability, _ = compute_desirability(  # type: ignore[arg-type]
            heuristic_result, desired_half_life, tolerance, weights, target_mode
        )
        return desirability

