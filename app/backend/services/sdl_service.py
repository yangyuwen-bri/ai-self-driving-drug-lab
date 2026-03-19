from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.backend.core.config import load_fixed_components
from app.backend.integrations.chemos_orchestrator import ChemOSOrchestrator
from app.backend.integrations.external_brains import integration_registry
from app.backend.integrations.opentrons_executor import OpentronsExecutor
from app.backend.models.schemas import (
    ExperimentRecord,
    RoundSummary,
    SDLRequest,
    SDLRunSummary,
)
from app.backend.optimization.baybe_adapter import BayBEOptimizerAdapter
from app.backend.optimization.objectives import compute_desirability
from app.backend.reporting.report_generator import ExperimentReportGenerator
from app.backend.simulation.drug_lab_simulator import DrugFormulationSimulator
from app.backend.storage.sqlite_store import SQLiteExperimentStore


class SDLService:
    def __init__(self) -> None:
        self.store = SQLiteExperimentStore()
        self.simulator = DrugFormulationSimulator()
        self.optimizer = BayBEOptimizerAdapter()
        self.reporter = ExperimentReportGenerator()
        self.opentrons = OpentronsExecutor()
        self.chemos = ChemOSOrchestrator()

    def run_closed_loop(self, request: SDLRequest) -> SDLRunSummary:
        run_id = f"sdl-{uuid4().hex[:10]}"
        started_at = datetime.now(UTC)
        fixed_components = load_fixed_components()
        history: list[ExperimentRecord] = []
        round_strategies: list[str] = []

        for round_index in range(1, request.max_rounds + 1):
            recommendation = self.optimizer.suggest(
                history=history,
                desired_half_life=request.desired_half_life,
                tolerance=request.tolerance,
                weights=request.weights,
                target_mode=request.target_mode,
                initial_random_samples=request.initial_random_samples,
                strategy=request.strategy,
            )
            round_strategies.append(recommendation.strategy)
            result = self.simulator.run(recommendation.parameters)
            desirability, error = compute_desirability(
                result=result,
                desired_half_life=request.desired_half_life,
                tolerance=request.tolerance,
                weights=request.weights,
                target_mode=request.target_mode,
            )
            result.desirability = desirability
            result.target_error = error

            record = ExperimentRecord(
                run_id=run_id,
                round_index=round_index,
                parameters=recommendation.parameters,
                result=result,
            )
            history.append(record)
            self.store.insert_experiment(record)

            if error <= request.tolerance:
                break

        best_record = max(history, key=lambda item: item.result.desirability)
        finished_at = datetime.now(UTC)
        status = "completed" if best_record.result.target_error <= request.tolerance else "max_rounds_reached"
        rounds = [
            RoundSummary(
                round_index=record.round_index,
                parameters=record.parameters,
                result=record.result,
                is_best=(record.round_index == best_record.round_index),
            )
            for record in history
        ]

        integration_status = {
            "opentrons": self.opentrons.build_protocol_payload(best_record.parameters)["status"],
            "chemos": self.chemos.describe()["mode"],
        }
        integration_status.update(integration_registry())

        strategy_used = round_strategies[0]
        if round_strategies[-1] != round_strategies[0]:
            strategy_used = f"{round_strategies[0]} -> {round_strategies[-1]}"

        summary = SDLRunSummary(
            run_id=run_id,
            status=status,
            desired_half_life=request.desired_half_life,
            tolerance=request.tolerance,
            strategy_used=strategy_used,
            best_parameters=best_record.parameters,
            best_result=best_record.result,
            rounds=rounds,
            report_path="",
            started_at=started_at,
            finished_at=finished_at,
            fixed_components=fixed_components,
            integration_status=integration_status,
        )
        summary.report_path = self.reporter.write(summary)
        self.store.upsert_run_summary(summary)
        return summary
