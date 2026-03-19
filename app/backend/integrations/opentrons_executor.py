from __future__ import annotations

from app.backend.models.schemas import ExperimentParameters


class OpentronsExecutor:
    """Phase 1 execution stub for mapping candidate parameters to OT-2/Flex protocols."""

    def build_protocol_payload(self, parameters: ExperimentParameters) -> dict:
        return {
            "platform": "Opentrons",
            "mode": "stub",
            "deck_setup": "96-well formulation screening plate",
            "liquid_transfers": parameters.model_dump(),
            "status": "ready_for_protocol_translation",
            "github": "https://github.com/Opentrons/opentrons",
        }

