from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from .types import Artifact, Measurement, ParameterVector, PlannerSuggestion


class CampaignStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ROUNDS_REACHED = "max_rounds_reached"


class RoundStatus(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    EXECUTED = "executed"
    MEASURED = "measured"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class CampaignConfig:
    campaign_id: str
    scenario_name: str
    target: dict[str, float]
    tolerance: float
    max_rounds: int
    strategy: str = "auto"
    status: CampaignStatus = CampaignStatus.DRAFT
    current_round: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None


@dataclass(slots=True)
class CampaignRoundRecord:
    campaign_id: str
    round_index: int
    parameters: ParameterVector
    measurement: Measurement | None = None
    planner_name: str = ""
    suggestion: PlannerSuggestion | None = None
    artifacts: list[Artifact] = field(default_factory=list)
    target_error: float | None = None
    status: RoundStatus = RoundStatus.CREATED
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
