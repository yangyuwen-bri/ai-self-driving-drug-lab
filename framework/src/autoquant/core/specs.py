from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParameterSpec:
    name: str
    lower: float
    upper: float
    unit: str = ""
    description: str = ""


@dataclass(slots=True)
class ObjectiveSpec:
    name: str
    mode: str
    target: float | None = None
    weight: float = 1.0
    unit: str = ""
    tolerance: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConstraintSpec:
    name: str
    description: str


@dataclass(slots=True)
class ScenarioSpec:
    name: str
    parameters: list[ParameterSpec]
    objectives: list[ObjectiveSpec]
    fixed_components: dict[str, object] = field(default_factory=dict)
    constraints: list[ConstraintSpec] = field(default_factory=list)
