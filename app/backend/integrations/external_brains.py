from __future__ import annotations


def integration_registry() -> dict:
    return {
        "baybe": "primary optimizer adapter wired; installs from https://github.com/emdgroup/baybe",
        "olympus": "benchmark hook reserved for planner comparison; https://github.com/aspuru-guzik-group/olympus",
        "atlas": "phase 3 advanced planner hook reserved; https://github.com/aspuru-guzik-group/atlas",
        "madsci": "cloud orchestration hook reserved; https://github.com/AD-SDL/MADSci",
        "awesome_sdl": "reference knowledge base; https://github.com/AccelerationConsortium/awesome-self-driving-labs",
    }

