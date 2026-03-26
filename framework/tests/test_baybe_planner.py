from __future__ import annotations

import unittest

from autoquant.core import CampaignConfig, CampaignRoundRecord, Measurement, ObjectiveSpec, ParameterSpec, ScenarioSpec
from autoquant.planners import BayBEPlanner, baybe_available


@unittest.skipUnless(baybe_available(), "BayBE is not installed")
class BayBEPlannerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = ScenarioSpec(
            name="toy_baybe",
            parameters=[
                ParameterSpec("temperature", 20.0, 80.0),
                ParameterSpec("aux_ratio", 0.5, 5.0),
            ],
            objectives=[
                ObjectiveSpec("half_life", mode="match_bell", target=12.0, tolerance=0.5, weight=0.7),
                ObjectiveSpec(
                    "stability_index",
                    mode="maximize",
                    weight=0.3,
                    metadata={"lower_bound": 40.0, "upper_bound": 100.0},
                ),
            ],
        )
        self.campaign = CampaignConfig(
            campaign_id="baybe-test",
            scenario_name=self.scenario.name,
            target={"half_life": 12.0},
            tolerance=0.5,
            max_rounds=6,
            strategy="baybe",
        )

    def test_propose_returns_in_bounds_without_history(self) -> None:
        planner = BayBEPlanner(initial_random_samples=2)
        suggestion = planner.propose(self.scenario, self.campaign, history=[])
        self.assertEqual(suggestion.planner_name, "baybe")
        self.assertIn(suggestion.metadata["phase"], {"baybe_random", "baybe_botorch"})
        self.assertGreaterEqual(suggestion.parameters["temperature"], 20.0)
        self.assertLessEqual(suggestion.parameters["temperature"], 80.0)
        self.assertGreaterEqual(suggestion.parameters["aux_ratio"], 0.5)
        self.assertLessEqual(suggestion.parameters["aux_ratio"], 5.0)

    def test_propose_consumes_history(self) -> None:
        planner = BayBEPlanner(initial_random_samples=1)
        history = [
            CampaignRoundRecord(
                campaign_id="baybe-test",
                round_index=1,
                parameters={"temperature": 42.0, "aux_ratio": 1.5},
                planner_name="baybe",
                measurement=Measurement(
                    values={"half_life": 11.8, "stability_index": 82.0},
                    source="simulation",
                ),
            )
        ]
        suggestion = planner.propose(self.scenario, self.campaign, history=history)
        self.assertEqual(suggestion.planner_name, "baybe")
        self.assertIn("phase", suggestion.metadata)
        self.assertIn("history_size", suggestion.metadata)
        self.assertEqual(suggestion.metadata["history_size"], 1)


if __name__ == "__main__":
    unittest.main()
