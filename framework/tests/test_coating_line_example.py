from __future__ import annotations

import unittest

from autoquant.core import CampaignConfig, Measurement
from autoquant.executors import NoOpExecutor
from autoquant.examples.coating_line.simulator import CoatingLineSimulator
from autoquant.examples.coating_line.spec import COATING_LINE_SCENARIO
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.modeling import InMemoryModelRegistry
from autoquant.orchestration import SequentialOrchestrator
from autoquant.planners import AdaptivePlanner, BayBEPlanner, RandomPlanner, baybe_available
from autoquant.storage import InMemoryCampaignStore


class CoatingLineExampleTest(unittest.TestCase):
    def test_coating_line_example_runs_end_to_end(self) -> None:
        simulator = CoatingLineSimulator()

        def measure(scenario, campaign, suggestion, artifacts) -> Measurement:
            measurement = simulator.run(suggestion.parameters)
            measurement.metadata["artifact_count"] = len(artifacts)
            return measurement

        planners = {"random": RandomPlanner(seed=31)}
        if baybe_available():
            planners["baybe"] = BayBEPlanner(initial_random_samples=2)

        campaign = CampaignConfig(
            campaign_id="coating-line-test",
            scenario_name=COATING_LINE_SCENARIO.name,
            target={"coating_thickness": 85.0},
            tolerance=3.0,
            max_rounds=5,
            strategy="simulation_first",
            metadata={"example": "coating_line"},
        )
        store = InMemoryCampaignStore()
        registry = InMemoryModelRegistry()
        orchestrator = SequentialOrchestrator(
            planner=AdaptivePlanner(planners=planners, model_registry=registry, warmup_rounds_per_planner=1),
            executor=NoOpExecutor(),
            feedback_provider=SyntheticFeedbackProvider(measure),
            store=store,
            model_registry=registry,
        )

        history = orchestrator.run_campaign(COATING_LINE_SCENARIO, campaign)

        self.assertTrue(history)
        self.assertEqual(campaign.current_round, len(history))
        self.assertIn(campaign.status.value, {"completed", "max_rounds_reached"})
        self.assertTrue(all(record.measurement is not None for record in history))
        self.assertTrue(all("coating_thickness" in record.measurement.values for record in history if record.measurement))
        self.assertTrue(registry.summarize())


if __name__ == "__main__":
    unittest.main()
