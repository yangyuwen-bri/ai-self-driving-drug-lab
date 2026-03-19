from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = Path(os.getenv("SDL_REPORT_DIR", ROOT_DIR / "outputs"))
DB_PATH = Path(os.getenv("SDL_DB_PATH", OUTPUT_DIR / "sdl_lab.db"))


PARAMETER_BOUNDS: Dict[str, tuple[float, float]] = {
    "temperature": (20.0, 80.0),
    "humidity": (40.0, 80.0),
    "aux1_ratio": (0.5, 5.0),
    "aux2_ratio": (0.0, 3.0),
    "duration": (60.0, 300.0),
    "stirring_speed": (100.0, 1000.0),
    "pH": (4.0, 9.0),
    "solvent_concentration": (10.0, 50.0),
}


TARGET_COLUMNS: List[str] = [
    "half_life",
    "solubility",
    "stability_index",
    "dissolution_rate",
    "yield_percent",
]


@dataclass(frozen=True)
class DefaultObjectiveConfig:
    half_life_weight: float = 0.6
    stability_weight: float = 0.3
    solubility_weight: float = 0.1


def load_fixed_components() -> dict:
    with (DATA_DIR / "fixed_components.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_runtime_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

