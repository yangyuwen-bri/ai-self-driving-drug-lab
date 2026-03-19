from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.backend.core.config import PARAMETER_BOUNDS


class ObjectiveWeights(BaseModel):
    half_life: float = 0.6
    stability_index: float = 0.3
    solubility: float = 0.1

    @field_validator("*")
    @classmethod
    def positive_weight(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Objective weights must be non-negative.")
        return value


class ExperimentParameters(BaseModel):
    temperature: float
    humidity: float
    aux1_ratio: float
    aux2_ratio: float
    duration: float
    stirring_speed: float
    pH: float
    solvent_concentration: float

    @field_validator("*")
    @classmethod
    def within_bounds(cls, value: float, info) -> float:
        lower, upper = PARAMETER_BOUNDS[info.field_name]
        if not (lower <= value <= upper):
            raise ValueError(f"{info.field_name} must be within [{lower}, {upper}]")
        return float(value)

    def as_feature_vector(self) -> List[float]:
        return [getattr(self, key) for key in PARAMETER_BOUNDS]

    def as_dict(self) -> Dict[str, float]:
        return self.model_dump()


class ExperimentResult(BaseModel):
    half_life: float
    solubility: float
    stability_index: float
    dissolution_rate: float
    yield_percent: float
    desirability: float = 0.0
    target_error: float = 0.0
    source: Literal["simulation", "robot"] = "simulation"


class ExperimentRecord(BaseModel):
    run_id: str
    round_index: int
    parameters: ExperimentParameters
    result: ExperimentResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SDLRequest(BaseModel):
    desired_half_life: float = Field(default=12.0, ge=1.0, le=48.0)
    target_mode: Literal["single", "multi"] = "multi"
    max_rounds: int = Field(default=8, ge=1, le=30)
    tolerance: float = Field(default=0.5, ge=0.05, le=5.0)
    weights: ObjectiveWeights = Field(default_factory=ObjectiveWeights)
    initial_random_samples: int = Field(default=6, ge=3, le=30)
    strategy: Literal["baybe", "surrogate"] = "baybe"


class RoundSummary(BaseModel):
    round_index: int
    parameters: ExperimentParameters
    result: ExperimentResult
    is_best: bool = False


class SDLRunSummary(BaseModel):
    run_id: str
    status: Literal["completed", "max_rounds_reached"]
    desired_half_life: float
    tolerance: float
    strategy_used: str
    best_parameters: ExperimentParameters
    best_result: ExperimentResult
    rounds: List[RoundSummary]
    report_path: str
    started_at: datetime
    finished_at: datetime
    fixed_components: dict
    integration_status: Dict[str, str]
