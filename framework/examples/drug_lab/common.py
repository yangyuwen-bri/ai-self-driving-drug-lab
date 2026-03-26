from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Iterable

from autoquant.core.specs import ObjectiveSpec, ScenarioSpec


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = Path(__file__).resolve().parent


def ensure_src_on_path() -> None:
    import sys

    src_path = str(ROOT / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def normalized_ramp(value: float, low: float, high: float) -> float:
    clipped = min(max(value, low), high)
    return (clipped - low) / max(high - low, 1e-9)


def bell_score(value: float, target: float, tolerance: float) -> float:
    scaled = (value - target) / max(tolerance, 1e-9)
    return math.exp(-0.5 * scaled * scaled)


def compute_desirability(
    values: dict[str, float],
    target: dict[str, float],
    objectives: Iterable[ObjectiveSpec],
) -> float:
    components: list[tuple[float, float]] = []
    for objective in objectives:
        name = objective.name
        if name not in values:
            continue
        if objective.mode == "match_bell":
            score = bell_score(
                values[name],
                target[name],
                objective.tolerance or 0.5,
            )
        elif objective.mode == "maximize":
            if name == "stability_index":
                score = normalized_ramp(values[name], 40.0, 100.0)
            elif name == "solubility":
                score = normalized_ramp(values[name], 2.0, 35.0)
            else:
                score = normalized_ramp(values[name], 0.0, 1.0)
        else:
            raise ValueError(f"Unsupported objective mode: {objective.mode}")
        components.append((score, objective.weight))
    total_weight = sum(weight for _, weight in components) or 1.0
    return sum(score * weight for score, weight in components) / total_weight


def sample_parameters(scenario: ScenarioSpec, rng: random.Random) -> dict[str, float]:
    return {
        spec.name: round(rng.uniform(spec.lower, spec.upper), 4)
        for spec in scenario.parameters
    }
