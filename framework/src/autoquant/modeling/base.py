from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from autoquant.core.campaigns import CampaignRoundRecord


@dataclass(slots=True)
class PlannerScore:
    planner_name: str
    avg_error: float
    success_rate: float
    runs_count: int


class ModelRegistry(Protocol):
    def record_round(self, round_record: CampaignRoundRecord) -> None:
        ...

    def summarize(self) -> list[PlannerScore]:
        ...

