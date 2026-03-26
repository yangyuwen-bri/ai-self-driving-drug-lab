from __future__ import annotations

import unittest

from autoquant.core import CampaignConfig, CampaignRoundRecord, ParameterSpec, PlannerSuggestion, ScenarioSpec
from autoquant.modeling import InMemoryModelRegistry
from autoquant.planners import AdaptivePlanner, Planner


class _StubPlanner(Planner):
    def __init__(self, name: str) -> None:
        self.name = name

    def propose(self, scenario, campaign, history):
        return PlannerSuggestion(
            planner_name=self.name,
            parameters={parameter.name: parameter.lower for parameter in scenario.parameters},
            rationale=f"from {self.name}",
        )


class AdaptivePlannerTest(unittest.TestCase):
    def test_warmup_then_select_by_history(self) -> None:
        scenario = ScenarioSpec(
            name="toy",
            parameters=[ParameterSpec("x", 0.0, 1.0)],
            objectives=[],
        )
        campaign = CampaignConfig(
            campaign_id="toy-campaign",
            scenario_name="toy",
            target={"y": 1.0},
            tolerance=0.1,
            max_rounds=4,
        )
        registry = InMemoryModelRegistry()
        planner = AdaptivePlanner(
            planners={
                "alpha": _StubPlanner("alpha"),
                "beta": _StubPlanner("beta"),
            },
            model_registry=registry,
            warmup_rounds_per_planner=1,
        )

        first = planner.propose(scenario, campaign, history=[])
        self.assertEqual(first.planner_name, "alpha")
        self.assertEqual(first.metadata["selection_reason"], "warmup exploration")

        alpha_round = CampaignRoundRecord(
            campaign_id="toy-campaign",
            round_index=1,
            parameters={"x": 0.0},
            planner_name="alpha",
            target_error=0.5,
            metadata={"tolerance": 0.1},
        )
        registry.record_round(alpha_round)
        second = planner.propose(scenario, campaign, history=[alpha_round])
        self.assertEqual(second.planner_name, "beta")

        beta_round = CampaignRoundRecord(
            campaign_id="toy-campaign",
            round_index=2,
            parameters={"x": 0.0},
            planner_name="beta",
            target_error=0.2,
            metadata={"tolerance": 0.1},
        )
        registry.record_round(beta_round)
        third = planner.propose(scenario, campaign, history=[alpha_round, beta_round])
        self.assertEqual(third.planner_name, "beta")
        self.assertEqual(third.metadata["selection_reason"], "selected by historical planner score")


if __name__ == "__main__":
    unittest.main()
