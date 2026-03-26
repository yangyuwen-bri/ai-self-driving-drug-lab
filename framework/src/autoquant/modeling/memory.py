from __future__ import annotations

from autoquant.core.campaigns import CampaignRoundRecord
from autoquant.modeling.base import ModelRegistry, PlannerScore


class InMemoryModelRegistry(ModelRegistry):
    def __init__(self) -> None:
        self._rounds: list[CampaignRoundRecord] = []

    def record_round(self, round_record: CampaignRoundRecord) -> None:
        self._rounds.append(round_record)

    def summarize(self) -> list[PlannerScore]:
        grouped: dict[str, list[CampaignRoundRecord]] = {}
        for round_record in self._rounds:
            grouped.setdefault(round_record.planner_name or "unknown", []).append(round_record)

        scores: list[PlannerScore] = []
        for planner_name, rounds in grouped.items():
            valid_errors = [
                round_record.target_error
                for round_record in rounds
                if round_record.target_error is not None
            ]
            avg_error = sum(valid_errors) / len(valid_errors) if valid_errors else 0.0
            successful = [
                round_record
                for round_record in rounds
                if round_record.target_error is not None
                and round_record.target_error <= round_record.metadata.get("tolerance", float("inf"))
            ]
            scores.append(
                PlannerScore(
                    planner_name=planner_name,
                    avg_error=avg_error,
                    success_rate=(len(successful) / len(rounds)) if rounds else 0.0,
                    runs_count=len(rounds),
                )
            )
        return sorted(scores, key=lambda item: (item.avg_error, -item.success_rate, -item.runs_count))
