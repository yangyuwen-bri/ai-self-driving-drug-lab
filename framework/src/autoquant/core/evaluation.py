from __future__ import annotations

import math

from autoquant.core.specs import ScenarioSpec
from autoquant.core.types import Measurement, compute_target_error


def bell_score(value: float, target: float, tolerance: float) -> float:
    scaled = (value - target) / max(tolerance, 1e-9)
    return float(math.exp(-0.5 * scaled * scaled))


def maximize_score(value: float, lower: float, upper: float) -> float:
    clipped = min(max(value, lower), upper)
    return float((clipped - lower) / max(upper - lower, 1e-9))


def evaluate_measurement(
    scenario: ScenarioSpec,
    target: dict[str, float],
    measurement: Measurement,
) -> Measurement:
    weighted_total = 0.0
    weight_total = 0.0
    objective_scores: dict[str, float] = {}

    for objective in scenario.objectives:
        observed = measurement.values.get(objective.name)
        if observed is None:
            continue

        if objective.mode == "match_bell":
            target_value = target.get(objective.name, objective.target)
            if target_value is None:
                continue
            tolerance = objective.tolerance or 1.0
            score = bell_score(observed, target_value, tolerance)
        elif objective.mode == "maximize":
            lower = float(objective.metadata.get("lower_bound", 0.0))
            upper = float(objective.metadata.get("upper_bound", max(observed, 1.0)))
            score = maximize_score(observed, lower, upper)
        elif objective.mode == "minimize":
            upper = float(objective.metadata.get("upper_bound", max(observed, 1.0)))
            score = 1.0 - maximize_score(observed, 0.0, upper)
        else:
            continue

        objective_scores[objective.name] = score
        weighted_total += score * objective.weight
        weight_total += objective.weight

    measurement.target_error = compute_target_error(target, measurement)
    measurement.objective_score = float(weighted_total / max(weight_total, 1e-9)) if weight_total else None
    measurement.metadata.setdefault("objective_scores", objective_scores)
    return measurement
