from __future__ import annotations

from dataclasses import replace

from autoquant.core.campaigns import CampaignConfig, CampaignRoundRecord
from autoquant.storage.base import CampaignStore


class InMemoryCampaignStore(CampaignStore):
    """Simple in-memory store for local runs, examples, and smoke tests."""

    def __init__(self) -> None:
        self._campaigns: dict[str, CampaignConfig] = {}
        self._rounds: dict[str, dict[int, CampaignRoundRecord]] = {}

    def save_campaign(self, campaign: CampaignConfig) -> None:
        self._campaigns[campaign.campaign_id] = replace(campaign)

    def get_campaign(self, campaign_id: str) -> CampaignConfig | None:
        campaign = self._campaigns.get(campaign_id)
        return replace(campaign) if campaign is not None else None

    def save_round(self, round_record: CampaignRoundRecord) -> None:
        self._rounds.setdefault(round_record.campaign_id, {})[round_record.round_index] = replace(round_record)

    def list_campaigns(self) -> list[CampaignConfig]:
        return [replace(campaign) for campaign in self._campaigns.values()]

    def list_rounds(self, campaign_id: str) -> list[CampaignRoundRecord]:
        rounds = self._rounds.get(campaign_id, {})
        return [replace(round_record) for _, round_record in sorted(rounds.items())]
