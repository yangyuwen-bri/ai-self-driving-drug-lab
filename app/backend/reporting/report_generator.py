from __future__ import annotations

import json
from pathlib import Path

from app.backend.core.config import OUTPUT_DIR, ensure_runtime_dirs
from app.backend.models.schemas import SDLRunSummary


class ExperimentReportGenerator:
    def write(self, summary: SDLRunSummary) -> str:
        ensure_runtime_dirs()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        markdown_path = Path(OUTPUT_DIR) / f"{summary.run_id}_report.md"
        json_path = Path(OUTPUT_DIR) / f"{summary.run_id}_report.json"

        lines = [
            f"# SDL Run Report: {summary.run_id}",
            "",
            f"- Status: {summary.status}",
            f"- Desired half-life: {summary.desired_half_life:.2f} h",
            f"- Tolerance: {summary.tolerance:.2f}",
            f"- Strategy used: {summary.strategy_used}",
            f"- Started at: {summary.started_at.isoformat()}",
            f"- Finished at: {summary.finished_at.isoformat()}",
            "",
            "## Best Parameters",
            "",
        ]
        for key, value in summary.best_parameters.model_dump().items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Best Result", ""])
        for key, value in summary.best_result.model_dump().items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Fixed Components", ""])
        for key, value in summary.fixed_components.items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Integration Status", ""])
        for key, value in summary.integration_status.items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Round Trace", ""])
        for round_summary in summary.rounds:
            marker = " [BEST]" if round_summary.is_best else ""
            lines.append(
                f"- Round {round_summary.round_index}{marker}: half_life={round_summary.result.half_life:.3f}, "
                f"desirability={round_summary.result.desirability:.4f}, error={round_summary.result.target_error:.4f}"
            )

        markdown_path.write_text("\n".join(lines), encoding="utf-8")
        json_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
        return str(markdown_path)

