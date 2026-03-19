from __future__ import annotations

import unittest

from app.backend.models.schemas import SDLRequest
from app.backend.services.sdl_service import SDLService


class SDLLoopTests(unittest.TestCase):
    def test_closed_loop_returns_summary_and_rounds_with_baybe(self) -> None:
        service = SDLService()
        summary = service.run_closed_loop(
            SDLRequest(
                desired_half_life=12.0,
                tolerance=0.5,
                max_rounds=8,
                target_mode="multi",
                strategy="baybe",
            )
        )
        self.assertGreaterEqual(len(summary.rounds), 1)
        self.assertLessEqual(len(summary.rounds), 8)
        self.assertTrue(summary.report_path.endswith(".md"))
        self.assertGreater(summary.best_result.desirability, 0.0)
        self.assertIn("baybe", summary.strategy_used)

    def test_surrogate_strategy_remains_available_for_benchmarking(self) -> None:
        service = SDLService()
        summary = service.run_closed_loop(
            SDLRequest(
                desired_half_life=12.0,
                tolerance=0.5,
                max_rounds=8,
                target_mode="multi",
                strategy="surrogate",
            )
        )
        self.assertGreaterEqual(len(summary.rounds), 1)
        self.assertTrue(summary.report_path.endswith(".md"))
        self.assertIn("surrogate", summary.strategy_used)


if __name__ == "__main__":
    unittest.main()
