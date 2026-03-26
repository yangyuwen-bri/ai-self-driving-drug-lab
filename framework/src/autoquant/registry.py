from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from autoquant.executors import NoOpExecutor
from autoquant.feedback import SyntheticFeedbackProvider
from autoquant.planners import AdaptivePlanner, RandomPlanner
from autoquant.scenarios import list_builtin_scenarios, load_builtin_scenario


T = TypeVar("T")


@dataclass(slots=True)
class RegistryEntry(Generic[T]):
    name: str
    factory: Callable[..., T]
    description: str = ""


class FactoryRegistry(Generic[T]):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._entries: dict[str, RegistryEntry[T]] = {}

    def register(self, name: str, factory: Callable[..., T], description: str = "") -> None:
        self._entries[name] = RegistryEntry(name=name, factory=factory, description=description)

    def create(self, name: str, **kwargs: Any) -> T:
        entry = self._entries.get(name)
        if entry is None:
            available = ", ".join(sorted(self._entries)) or "(none)"
            raise KeyError(f"Unknown {self.kind} '{name}'. Available: {available}")
        return entry.factory(**kwargs)

    def names(self) -> list[str]:
        return sorted(self._entries)

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": entry.name, "description": entry.description}
            for entry in sorted(self._entries.values(), key=lambda item: item.name)
        ]


def build_planner_registry() -> FactoryRegistry[Any]:
    registry = FactoryRegistry[Any]("planner")
    registry.register("random", RandomPlanner, "Uniform random planner over parameter bounds.")
    registry.register(
        "adaptive",
        AdaptivePlanner,
        "Meta-planner that selects among child planners using warmup and score history.",
    )
    try:
        from autoquant.planners import BayBEPlanner
    except Exception:
        pass
    else:
        registry.register("baybe", BayBEPlanner, "BayBE-backed closed-loop planner.")
    return registry


def build_executor_registry() -> FactoryRegistry[Any]:
    registry = FactoryRegistry[Any]("executor")
    registry.register("noop", NoOpExecutor, "No-op executor for simulation and dry runs.")
    return registry


def build_feedback_registry() -> FactoryRegistry[Any]:
    registry = FactoryRegistry[Any]("feedback")
    registry.register(
        "synthetic",
        SyntheticFeedbackProvider,
        "Synthetic feedback adapter wrapping a Python measure function.",
    )
    return registry


def list_registered_scenarios() -> list[str]:
    return list_builtin_scenarios()


def create_scenario(name: str):
    return load_builtin_scenario(name)
