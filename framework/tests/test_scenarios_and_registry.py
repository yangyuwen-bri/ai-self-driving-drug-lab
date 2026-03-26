from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.planners import RandomPlanner
from autoquant.registry import (
    build_executor_registry,
    build_feedback_registry,
    build_planner_registry,
    create_scenario,
    list_registered_scenarios,
)
from autoquant.scenarios import dumps_scenario_json, load_scenario_file


class ScenarioAndRegistryTest(unittest.TestCase):
    def test_builtin_scenarios_load_and_roundtrip(self) -> None:
        self.assertIn("drug_lab", list_registered_scenarios())
        scenario = create_scenario("drug_lab")
        rendered = dumps_scenario_json(scenario)
        self.assertIn('"name": "drug_lab_demo"', rendered)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "scenario.json"
            path.write_text(rendered, encoding="utf-8")
            loaded = load_scenario_file(path)
        self.assertEqual(loaded.name, scenario.name)
        self.assertEqual(len(loaded.parameters), len(scenario.parameters))
        self.assertEqual(len(loaded.objectives), len(scenario.objectives))

    def test_registries_create_known_components(self) -> None:
        planners = build_planner_registry()
        executors = build_executor_registry()
        feedback = build_feedback_registry()

        self.assertIsInstance(planners.create("random", seed=7), RandomPlanner)
        self.assertIsInstance(executors.create("noop"), NoOpExecutor)
        self.assertIsInstance(feedback.create("synthetic", measure_fn=lambda *args, **kwargs: None), SyntheticFeedbackProvider)


if __name__ == "__main__":
    unittest.main()
