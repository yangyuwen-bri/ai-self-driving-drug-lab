from __future__ import annotations

from abc import ABC, abstractmethod

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord


class CampaignStore(ABC):
    @abstractmethod
    def save_campaign(self, campaign: CampaignConfig) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_campaign(self, campaign_id: str) -> CampaignConfig | None:
        raise NotImplementedError

    @abstractmethod
    def save_round(self, round_record: CampaignRoundRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_campaigns(self) -> list[CampaignConfig]:
        raise NotImplementedError

    @abstractmethod
    def list_rounds(self, campaign_id: str) -> list[CampaignRoundRecord]:
        raise NotImplementedError
