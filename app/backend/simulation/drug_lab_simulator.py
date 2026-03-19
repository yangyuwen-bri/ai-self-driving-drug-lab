from __future__ import annotations

import hashlib
from typing import Dict

import numpy as np

from app.backend.models.schemas import ExperimentParameters, ExperimentResult


class DrugFormulationSimulator:
    """Digital twin for formulation development before routing to real hardware."""

    @staticmethod
    def _seed_from_parameters(parameters: ExperimentParameters) -> int:
        payload = "|".join(f"{k}:{v:.4f}" for k, v in parameters.as_dict().items())
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def run(self, parameters: ExperimentParameters) -> ExperimentResult:
        seed = self._seed_from_parameters(parameters)
        rng = np.random.default_rng(seed)

        t = parameters.temperature
        h = parameters.humidity
        aux1 = parameters.aux1_ratio
        aux2 = parameters.aux2_ratio
        duration = parameters.duration
        speed = parameters.stirring_speed
        ph = parameters.pH
        solvent = parameters.solvent_concentration

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
            + rng.normal(0, 0.18)
        )

        solubility = (
            4.0
            + 0.42 * solvent
            + 1.7 * aux1
            - 0.08 * aux2
            - 0.045 * max(t - 55.0, 0.0)
            - 0.4 * max(ph - 7.4, 0.0) ** 2
            + rng.normal(0, 0.25)
        )

        stability_index = (
            96.0
            - 0.022 * (t - 36.0) ** 2
            - 0.010 * (h - 52.0) ** 2
            - 1.7 * abs(ph - 6.0)
            + 2.2 * aux2
            - 0.004 * abs(duration - 180.0)
            + rng.normal(0, 0.35)
        )

        dissolution_rate = (
            0.35
            + 0.05 * aux1
            + 0.013 * solvent
            + 0.00025 * speed
            - 0.0009 * duration
            - 0.004 * aux2
            + rng.normal(0, 0.02)
        )

        yield_percent = (
            72.0
            + 0.05 * duration
            - 0.00006 * (speed - 600.0) ** 2
            - 0.018 * (t - 45.0) ** 2
            - 0.38 * (ph - 6.0) ** 2
            + 0.8 * aux2
            + rng.normal(0, 0.4)
        )

        return ExperimentResult(
            half_life=self._clip(half_life, 1.0, 30.0),
            solubility=self._clip(solubility, 0.5, 40.0),
            stability_index=self._clip(stability_index, 0.0, 100.0),
            dissolution_rate=self._clip(dissolution_rate, 0.01, 5.0),
            yield_percent=self._clip(yield_percent, 10.0, 99.5),
            source="simulation",
        )

    @staticmethod
    def _clip(value: float, lower: float, upper: float) -> float:
        return float(np.clip(value, lower, upper))

    def describe_real_hardware_mapping(self) -> Dict[str, str]:
        return {
            "phase_1": "Opentrons executor stub prepared for liquid-handling transfer and plate setup.",
            "phase_2": "ChemOS 2.0 orchestrator stub prepared for SiLA2 workflow execution.",
            "phase_3": "Atlas / MADSci hooks prepared for advanced planning and cloud orchestration.",
        }

