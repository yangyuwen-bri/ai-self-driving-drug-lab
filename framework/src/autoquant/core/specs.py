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

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "parameters": [
                {
                    "name": item.name,
                    "lower": item.lower,
                    "upper": item.upper,
                    "unit": item.unit,
                    "description": item.description,
                }
                for item in self.parameters
            ],
            "objectives": [
                {
                    "name": item.name,
                    "mode": item.mode,
                    "target": item.target,
                    "weight": item.weight,
                    "unit": item.unit,
                    "tolerance": item.tolerance,
                    "metadata": dict(item.metadata),
                }
                for item in self.objectives
            ],
            "fixed_components": dict(self.fixed_components),
            "constraints": [
                {
                    "name": item.name,
                    "description": item.description,
                }
                for item in self.constraints
            ],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ScenarioSpec":
        return cls(
            name=str(payload["name"]),
            parameters=[
                ParameterSpec(
                    name=str(item["name"]),
                    lower=float(item["lower"]),
                    upper=float(item["upper"]),
                    unit=str(item.get("unit", "")),
                    description=str(item.get("description", "")),
                )
                for item in payload.get("parameters", [])
            ],
            objectives=[
                ObjectiveSpec(
                    name=str(item["name"]),
                    mode=str(item["mode"]),
                    target=None if item.get("target") is None else float(item["target"]),
                    weight=float(item.get("weight", 1.0)),
                    unit=str(item.get("unit", "")),
                    tolerance=None if item.get("tolerance") is None else float(item["tolerance"]),
                    metadata=dict(item.get("metadata", {})),
                )
                for item in payload.get("objectives", [])
            ],
            fixed_components=dict(payload.get("fixed_components", {})),
            constraints=[
                ConstraintSpec(
                    name=str(item["name"]),
                    description=str(item.get("description", "")),
                )
                for item in payload.get("constraints", [])
            ],
        )
