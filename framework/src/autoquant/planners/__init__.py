from .adaptive import AdaptivePlanner
from .base import Planner
from .random import RandomPlanner

__all__ = ["AdaptivePlanner", "BayBEPlanner", "Planner", "RandomPlanner", "baybe_available"]


def __getattr__(name: str):
    if name in {"BayBEPlanner", "baybe_available"}:
        from .baybe import BayBEPlanner, baybe_available

        return {"BayBEPlanner": BayBEPlanner, "baybe_available": baybe_available}[name]
    raise AttributeError(name)
