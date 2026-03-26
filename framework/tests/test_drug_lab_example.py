from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / ".venv/bin/python"


class DrugLabExampleTest(unittest.TestCase):
    def test_drug_lab_example_runs(self) -> None:
        result = subprocess.run(
            [
                str(PYTHON),
                "-m",
                "autoquant.examples.drug_lab.run_example",
                "--target-half-life",
                "12.0",
                "--tolerance",
                "0.5",
                "--max-rounds",
                "6",
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": "framework/src"},
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["campaign"]["target"]["half_life"], 12.0)
        self.assertGreaterEqual(len(payload["rounds"]), 1)
        self.assertIn(payload["result"]["status"], {"completed", "max_rounds_reached"})


if __name__ == "__main__":
    unittest.main()
