from __future__ import annotations

import hashlib
import random

from autoquant.core.types import Measurement


class CoatingLineSimulator:
    """Synthetic industrial process twin for a coating-line optimization loop."""

    @staticmethod
    def _seed(parameters: dict[str, float]) -> int:
        payload = "|".join(f"{key}:{parameters[key]:.4f}" for key in sorted(parameters))
        return int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8], 16)

    def run(self, parameters: dict[str, float]) -> Measurement:
        rng = random.Random(self._seed(parameters))
        oven = parameters["oven_temperature"]
        speed = parameters["line_speed"]
        catalyst = parameters["catalyst_ratio"]
        airflow = parameters["dryer_flow"]
        pressure = parameters["pressure"]

        coating_thickness = (
            87.0
            - 0.020 * (oven - 185.0) ** 2
            - 0.50 * (speed - 13.0) ** 2
            + 7.5 * catalyst
            - 0.05 * (airflow - 55.0) ** 2
            + 1.2 * pressure
            + rng.gauss(0.0, 1.2)
        )
        adhesion_index = (
            92.0
            - 0.018 * (oven - 180.0) ** 2
            - 0.22 * (pressure - 3.2) ** 2
            + 3.0 * catalyst
            - 0.006 * (airflow - 50.0) ** 2
            + rng.gauss(0.0, 0.7)
        )
        throughput = (
            12.0
            + 4.6 * speed
            - 0.035 * (oven - 175.0) ** 2
            - 0.018 * (airflow - 45.0) ** 2
            + rng.gauss(0.0, 1.5)
        )
        defect_rate = (
            5.0
            + 0.012 * abs(oven - 185.0) ** 2
            + 0.020 * abs(pressure - 3.0) ** 2
            - 0.9 * catalyst
            + rng.gauss(0.0, 0.15)
        )
        return Measurement(
            values={
                "coating_thickness": max(40.0, min(130.0, coating_thickness)),
                "adhesion_index": max(0.0, min(100.0, adhesion_index)),
                "throughput": max(5.0, min(140.0, throughput)),
                "defect_rate": max(0.0, min(25.0, defect_rate)),
            },
            source="simulation",
        )
