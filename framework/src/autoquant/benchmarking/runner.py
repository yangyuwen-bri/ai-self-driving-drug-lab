from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from statistics import mean
from typing import Callable
from uuid import uuid4

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord, CampaignStatus
from autoquant.core.specs import ScenarioSpec
from autoquant.executors.base import Executor
from autoquant.feedback.base import FeedbackProvider
from autoquant.modeling.base import ModelRegistry
from autoquant.modeling.memory import InMemoryModelRegistry
from autoquant.orchestration.sequential import SequentialOrchestrator
from autoquant.planners.base import Planner
from autoquant.storage.base import CampaignStore
from autoquant.storage.memory import InMemoryCampaignStore


@dataclass(slots=True)
class BenchmarkTrialResult:
    planner_name: str
    replicate_index: int
    campaign_id: str
    status: str
    rounds_run: int
    best_round_index: int | None
    best_error: float | None
    best_objective_score: float | None


@dataclass(slots=True)
class BenchmarkPlannerSummary:
    planner_name: str
    trials_count: int
    success_rate: float
    avg_best_error: float
    avg_rounds_run: float
    avg_best_objective_score: float | None


@dataclass(slots=True)
class BenchmarkReport:
    scenario_name: str
    target: dict[str, float]
    tolerance: float
    replicates: int
    summaries: list[BenchmarkPlannerSummary]
    trials: list[BenchmarkTrialResult]


def _clone_campaign(template: CampaignConfig, planner_name: str, replicate_index: int) -> CampaignConfig:
    campaign = deepcopy(template)
    campaign.campaign_id = f"{template.campaign_id}-{planner_name}-{replicate_index + 1}-{uuid4().hex[:6]}"
    campaign.status = CampaignStatus.DRAFT
    campaign.current_round = 0
    campaign.finished_at = None
    campaign.metadata = {
        **template.metadata,
        "benchmark_planner": planner_name,
        "benchmark_replicate": replicate_index + 1,
    }
    return campaign


def _best_round(history: list[CampaignRoundRecord]) -> CampaignRoundRecord | None:
    candidates = [record for record in history if record.target_error is not None]
    if not candidates:
        return None
    return min(candidates, key=lambda record: record.target_error if record.target_error is not None else float("inf"))


def benchmark_planners(
    scenario: ScenarioSpec,
    campaign_template: CampaignConfig,
    planner_factories: dict[str, Callable[[], Planner]],
    executor_factory: Callable[[], Executor],
    feedback_factory: Callable[[], FeedbackProvider],
    replicates: int = 3,
    store_factory: Callable[[], CampaignStore] | None = None,
    registry_factory: Callable[[], ModelRegistry] | None = None,
) -> BenchmarkReport:
    trials: list[BenchmarkTrialResult] = []
    grouped: dict[str, list[BenchmarkTrialResult]] = {}

    for planner_name, planner_factory in planner_factories.items():
        for replicate_index in range(replicates):
            planner: Planner = planner_factory()
            store: CampaignStore = store_factory() if store_factory is not None else InMemoryCampaignStore()
            registry: ModelRegistry = (
                registry_factory() if registry_factory is not None else InMemoryModelRegistry()
            )
            campaign = _clone_campaign(campaign_template, planner_name, replicate_index)
            orchestrator = SequentialOrchestrator(
                planner=planner,
                executor=executor_factory(),
                feedback_provider=feedback_factory(),
                store=store,
                model_registry=registry,
            )
            history = orchestrator.run_campaign(scenario, campaign)
            best_round = _best_round(history)
            trial = BenchmarkTrialResult(
                planner_name=planner_name,
                replicate_index=replicate_index + 1,
                campaign_id=campaign.campaign_id,
                status=campaign.status.value,
                rounds_run=len(history),
                best_round_index=best_round.round_index if best_round is not None else None,
                best_error=best_round.target_error if best_round is not None else None,
                best_objective_score=(
                    best_round.measurement.objective_score
                    if best_round is not None and best_round.measurement is not None
                    else None
                ),
            )
            trials.append(trial)
            grouped.setdefault(planner_name, []).append(trial)

    summaries: list[BenchmarkPlannerSummary] = []
    for planner_name, planner_trials in grouped.items():
        successful = [trial for trial in planner_trials if trial.best_error is not None and trial.best_error <= campaign_template.tolerance]
        valid_errors = [trial.best_error for trial in planner_trials if trial.best_error is not None]
        valid_scores = [trial.best_objective_score for trial in planner_trials if trial.best_objective_score is not None]
        summaries.append(
            BenchmarkPlannerSummary(
                planner_name=planner_name,
                trials_count=len(planner_trials),
                success_rate=(len(successful) / len(planner_trials)) if planner_trials else 0.0,
                avg_best_error=mean(valid_errors) if valid_errors else float("inf"),
                avg_rounds_run=mean(trial.rounds_run for trial in planner_trials) if planner_trials else 0.0,
                avg_best_objective_score=mean(valid_scores) if valid_scores else None,
            )
        )
    summaries.sort(key=lambda item: (item.avg_best_error, -item.success_rate, item.avg_rounds_run))
    return BenchmarkReport(
        scenario_name=scenario.name,
        target=dict(campaign_template.target),
        tolerance=campaign_template.tolerance,
        replicates=replicates,
        summaries=summaries,
        trials=trials,
    )
