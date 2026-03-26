from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from autoquant.core.specs import ScenarioSpec


def list_builtin_scenarios() -> list[str]:
    root = files("autoquant.scenarios")
    return sorted(item.name[:-5] for item in root.iterdir() if item.name.endswith(".json"))


def load_builtin_scenario(name: str) -> ScenarioSpec:
    resource = files("autoquant.scenarios").joinpath(f"{name}.json")
    if not resource.is_file():
        available = ", ".join(list_builtin_scenarios()) or "(none)"
        raise FileNotFoundError(f"Unknown built-in scenario '{name}'. Available: {available}")
    payload = json.loads(resource.read_text(encoding="utf-8"))
    return ScenarioSpec.from_dict(payload)


def load_scenario_file(path: str | Path) -> ScenarioSpec:
    source = Path(path)
    suffix = source.suffix.lower()
    raw = source.read_text(encoding="utf-8")
    if suffix == ".json":
        payload = json.loads(raw)
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except Exception as exc:
            raise RuntimeError("YAML support requires PyYAML to be installed.") from exc
        payload = yaml.safe_load(raw)
    else:
        raise ValueError(f"Unsupported scenario file format: {source.suffix}")
    return ScenarioSpec.from_dict(payload)


def dumps_scenario_json(scenario: ScenarioSpec) -> str:
    return json.dumps(scenario.to_dict(), indent=2, ensure_ascii=False)
