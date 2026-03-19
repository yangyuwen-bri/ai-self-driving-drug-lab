from __future__ import annotations

from pprint import pprint

from app.backend.models.schemas import SDLRequest
from app.backend.services.sdl_service import SDLService


def main() -> None:
    service = SDLService()
    summary = service.run_closed_loop(
        SDLRequest(
            desired_half_life=12.0,
            tolerance=0.5,
            max_rounds=8,
            target_mode="multi",
            strategy="baybe",
        )
    )
    print(f"Run ID: {summary.run_id}")
    print(f"Status: {summary.status}")
    print("Best parameters:")
    pprint(summary.best_parameters.model_dump())
    print("Best result:")
    pprint(summary.best_result.model_dump())
    print(f"Report: {summary.report_path}")


if __name__ == "__main__":
    main()
