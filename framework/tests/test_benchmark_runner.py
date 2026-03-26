from __future__ import annotations

import unittest

from autoquant.benchmarking import benchmark_planners
from autoquant.core import CampaignConfig, Measurement, ParameterSpec, PlannerSuggestion, ScenarioSpec
from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.planners import Planner


class _GoodPlanner(Planner):
    def propose(self, scenario, campaign, history):
        return PlannerSuggestion(planner_name="good", parameters={"x": 2.0})


class _BadPlanner(Planner):
    def propose(self, scenario, campaign, history):
        return PlannerSuggestion(planner_name="bad", parameters={"x": 9.0})


class BenchmarkRunnerTest(unittest.TestCase):
    def test_benchmark_orders_better_planner_first(self) -> None:
        scenario = ScenarioSpec(
            name="toy",
            parameters=[ParameterSpec("x", 0.0, 10.0)],
            objectives=[],
        )
        campaign = CampaignConfig(
            campaign_id="toy-benchmark",
            scenario_name="toy",
            target={"y": 2.0},
            tolerance=0.5,
            max_rounds=1,
        )

        def measure(scenario, campaign, suggestion, artifacts):
            x = suggestion.parameters["x"]
            return Measurement(values={"y": x})

        report = benchmark_planners(
            scenario=scenario,
            campaign_template=campaign,
            planner_factories={
                "good": _GoodPlanner,
                "bad": _BadPlanner,
            },
            executor_factory=NoOpExecutor,
            feedback_factory=lambda: SyntheticFeedbackProvider(measure),
            replicates=2,
        )

        self.assertEqual(len(report.summaries), 2)
        self.assertEqual(report.summaries[0].planner_name, "good")
        self.assertLess(report.summaries[0].avg_best_error, report.summaries[1].avg_best_error)
        self.assertEqual(len(report.trials), 4)
        self.assertIn("summaries", report.to_dict())
        self.assertIn("| Planner |", report.to_markdown())


if __name__ == "__main__":
    unittest.main()
