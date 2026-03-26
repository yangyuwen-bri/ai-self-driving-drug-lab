from __future__ import annotations

import hashlib
import random

from autoquant.core.types import Measurement


class DrugLabSimulator:
    """Standalone digital twin for the framework example."""

    @staticmethod
    def _seed_from_parameters(parameters: dict[str, float]) -> int:
        payload = "|".join(f"{key}:{parameters[key]:.4f}" for key in sorted(parameters))
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def run(self, parameters: dict[str, float]) -> Measurement:
        rng = random.Random(self._seed_from_parameters(parameters))
        t = parameters["temperature"]
        h = parameters["humidity"]
        aux1 = parameters["aux1_ratio"]
        aux2 = parameters["aux2_ratio"]
        duration = parameters["duration"]
        speed = parameters["stirring_speed"]
        ph = parameters["pH"]
        solvent = parameters["solvent_concentration"]

        half_life = (
            18.0
            - 0.012 * (t - 42.0) ** 2
            - 0.004 * (h - 58.0) ** 2
            - 0.38 * (ph - 6.2) ** 2
            - 0.000018 * (speed - 520.0) ** 2
            + 0.55 * aux2
            + 0.14 * aux1
            + 0.012 * duration
            - 0.006 * solvent
            + rng.gauss(0.0, 0.18)
        )
        solubility = (
            4.0
            + 0.42 * solvent
            + 1.7 * aux1
            - 0.08 * aux2
            - 0.045 * max(t - 55.0, 0.0)
            - 0.4 * max(ph - 7.4, 0.0) ** 2
            + rng.gauss(0.0, 0.25)
        )
        stability_index = (
            96.0
            - 0.022 * (t - 36.0) ** 2
            - 0.010 * (h - 52.0) ** 2
            - 1.7 * abs(ph - 6.0)
            + 2.2 * aux2
            - 0.004 * abs(duration - 180.0)
            + rng.gauss(0.0, 0.35)
        )
        dissolution_rate = (
            0.35
            + 0.05 * aux1
            + 0.013 * solvent
            + 0.00025 * speed
            - 0.0009 * duration
            - 0.004 * aux2
            + rng.gauss(0.0, 0.02)
        )
        yield_percent = (
            72.0
            + 0.05 * duration
            - 0.00006 * (speed - 600.0) ** 2
            - 0.018 * (t - 45.0) ** 2
            - 0.38 * (ph - 6.0) ** 2
            + 0.8 * aux2
            + rng.gauss(0.0, 0.4)
        )
        return Measurement(
            values={
                "half_life": max(1.0, min(30.0, half_life)),
                "solubility": max(0.5, min(40.0, solubility)),
                "stability_index": max(0.0, min(100.0, stability_index)),
                "dissolution_rate": max(0.01, min(5.0, dissolution_rate)),
                "yield_percent": max(10.0, min(99.5, yield_percent)),
            },
            source="simulation",
        )
