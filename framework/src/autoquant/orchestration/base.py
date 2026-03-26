from __future__ import annotations

from abc import ABC, abstractmethod

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.core.specs import ScenarioSpec


class Orchestrator(ABC):
    @abstractmethod
    def run_campaign(
        self,
        scenario: ScenarioSpec,
        campaign: CampaignConfig,
    ) -> list[CampaignRoundRecord]:
        raise NotImplementedError

