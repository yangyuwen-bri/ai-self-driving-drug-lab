from __future__ import annotations

from datetime import UTC, datetime

from autoquant.core import evaluate_measurement
from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord, CampaignStatus, RoundStatus
from autoquant.core.specs import ScenarioSpec
from autoquant.executors.base import Executor
from autoquant.feedback.base import FeedbackProvider
from autoquant.modeling.base import ModelRegistry
from autoquant.modeling.memory import InMemoryModelRegistry
from autoquant.orchestration.base import Orchestrator
from autoquant.planners.base import Planner
from autoquant.storage.base import CampaignStore


class SequentialOrchestrator(Orchestrator):
    """Minimal synchronous DMTA loop for local examples and framework smoke tests."""

    def __init__(
        self,
        planner: Planner,
        executor: Executor,
        feedback_provider: FeedbackProvider,
        store: CampaignStore,
        model_registry: ModelRegistry | None = None,
    ) -> None:
        self.planner = planner
        self.executor = executor
        self.feedback_provider = feedback_provider
        self.store = store
        self.model_registry = model_registry or InMemoryModelRegistry()

    def run_campaign(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
    ) -> list[CampaignRoundRecord]:
        live_campaign = campaign
        live_campaign.status = CampaignStatus.RUNNING
        self.store.save_campaign(live_campaign)

        for round_index in range(1, live_campaign.max_rounds + 1):
            history = self.store.list_rounds(live_campaign.campaign_id)
            suggestion = self.planner.propose(scenario, live_campaign, history)

            round_record = CampaignRoundRecord(
                campaign_id=live_campaign.campaign_id,
                round_index=round_index,
                parameters=suggestion.parameters,
                planner_name=suggestion.planner_name,
                suggestion=suggestion,
                status=RoundStatus.PLANNED,
                metadata={"tolerance": live_campaign.tolerance},
            )
            self.store.save_round(round_record)

            artifacts = self.executor.execute(scenario, live_campaign, suggestion)
            round_record.artifacts = artifacts
            round_record.status = RoundStatus.EXECUTED
            round_record.updated_at = datetime.now(UTC)
            self.store.save_round(round_record)

            measurement = self.feedback_provider.collect(scenario, live_campaign, suggestion, artifacts)
            measurement = evaluate_measurement(scenario, live_campaign.target, measurement)
            round_record.measurement = measurement
            round_record.target_error = measurement.target_error
            round_record.status = RoundStatus.MEASURED
            round_record.updated_at = datetime.now(UTC)
            self.store.save_round(round_record)

            round_record.status = RoundStatus.COMPLETED
            round_record.updated_at = datetime.now(UTC)
            self.store.save_round(round_record)
            self.model_registry.record_round(round_record)

            live_campaign.current_round = round_index
            self.store.save_campaign(live_campaign)

            if (
                round_record.target_error is not None
                and round_record.target_error <= live_campaign.tolerance
            ):
                live_campaign.status = CampaignStatus.COMPLETED
                live_campaign.finished_at = datetime.now(UTC)
                self.store.save_campaign(live_campaign)
                return self.store.list_rounds(live_campaign.campaign_id)

        live_campaign.status = CampaignStatus.MAX_ROUNDS_REACHED
        live_campaign.finished_at = datetime.now(UTC)
        self.store.save_campaign(live_campaign)
        return self.store.list_rounds(live_campaign.campaign_id)
