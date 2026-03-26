from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


ParameterVector = dict[str, float]


@dataclass(slots=True)
class Measurement:
    values: dict[str, float]
    source: str = "simulation"
    target_error: float | None = None
    objective_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, name: str, default: float | None = None) -> float | None:
        return self.values.get(name, default)


@dataclass(slots=True)
class PlannerSuggestion:
    planner_name: str
    parameters: ParameterVector
    score: float | None = None
    uncertainty: float | None = None
    rationale: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Artifact:
    artifact_type: str
    uri: str
    metadata: dict[str, Any] = field(default_factory=dict)


def compute_target_error(target: dict[str, float], measurement: Measurement) -> float:
    """Compute a simple scalar distance between target values and measured values.

    For a single objective this is absolute error. For multiple objectives it is RMSE
    over the target keys that are present in the measurement.
    """

    deltas = []
    for name, target_value in target.items():
        observed = measurement.values.get(name)
        if observed is None:
            continue
        deltas.append((float(observed) - float(target_value)) ** 2)
    if not deltas:
        return math.inf
    if len(deltas) == 1:
        return float(deltas[0] ** 0.5)
    return float((sum(deltas) / len(deltas)) ** 0.5)
