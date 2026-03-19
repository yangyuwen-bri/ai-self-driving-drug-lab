from __future__ import annotations

import math

from app.backend.models.schemas import ExperimentResult, ObjectiveWeights


def bell_desirability(value: float, target: float, tolerance: float) -> float:
    scaled = (value - target) / max(tolerance, 1e-6)
    return float(math.exp(-0.5 * scaled * scaled))


def max_desirability(value: float, low: float, high: float) -> float:
    clipped = min(max(value, low), high)
    return float((clipped - low) / max(high - low, 1e-6))


def compute_desirability(
    result: ExperimentResult,
    desired_half_life: float,
    tolerance: float,
    weights: ObjectiveWeights,
    target_mode: str,
) -> tuple[float, float]:
    target_error = abs(result.half_life - desired_half_life)
    if target_mode == "single":
        desirability = bell_desirability(result.half_life, desired_half_life, tolerance)
        return desirability, target_error

    components = {
        "half_life": bell_desirability(result.half_life, desired_half_life, tolerance),
        "stability_index": max_desirability(result.stability_index, 40.0, 100.0),
        "solubility": max_desirability(result.solubility, 2.0, 35.0),
    }
    weight_total = max(weights.half_life + weights.stability_index + weights.solubility, 1e-6)
    desirability = (
        components["half_life"] * weights.half_life
        + components["stability_index"] * weights.stability_index
        + components["solubility"] * weights.solubility
    ) / weight_total
    return float(desirability), float(target_error)

