from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import List

from app.backend.core.config import DB_PATH, ensure_runtime_dirs
from app.backend.models.schemas import ExperimentParameters, ExperimentRecord, ExperimentResult, SDLRunSummary


class SQLiteExperimentStore:
    def __init__(self) -> None:
        ensure_runtime_dirs()
        self.connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                desired_half_life REAL NOT NULL,
                tolerance REAL NOT NULL,
                strategy_used TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL,
                best_parameters_json TEXT NOT NULL,
                best_result_json TEXT NOT NULL,
                fixed_components_json TEXT NOT NULL,
                integration_status_json TEXT NOT NULL,
                report_path TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                round_index INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                result_json TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    def insert_experiment(self, record: ExperimentRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO experiments (run_id, round_index, created_at, parameters_json, result_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.run_id,
                record.round_index,
                record.created_at.isoformat(),
                json.dumps(record.parameters.model_dump()),
                json.dumps(record.result.model_dump()),
            ),
        )
        self.connection.commit()

    def list_run_experiments(self, run_id: str) -> List[ExperimentRecord]:
        rows = self.connection.execute(
            """
            SELECT run_id, round_index, created_at, parameters_json, result_json
            FROM experiments
            WHERE run_id = ?
            ORDER BY round_index ASC
            """,
            (run_id,),
        ).fetchall()
        records = []
        for row in rows:
            records.append(
                ExperimentRecord(
                    run_id=row["run_id"],
                    round_index=row["round_index"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    parameters=ExperimentParameters(**json.loads(row["parameters_json"])),
                    result=ExperimentResult(**json.loads(row["result_json"])),
                )
            )
        return records

    def upsert_run_summary(self, summary: SDLRunSummary) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_id, status, desired_half_life, tolerance, strategy_used,
                started_at, finished_at, best_parameters_json, best_result_json,
                fixed_components_json, integration_status_json, report_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                summary.run_id,
                summary.status,
                summary.desired_half_life,
                summary.tolerance,
                summary.strategy_used,
                summary.started_at.isoformat(),
                summary.finished_at.isoformat(),
                json.dumps(summary.best_parameters.model_dump()),
                json.dumps(summary.best_result.model_dump()),
                json.dumps(summary.fixed_components),
                json.dumps(summary.integration_status),
                summary.report_path,
            ),
        )
        self.connection.commit()

    def list_runs(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT run_id, status, desired_half_life, tolerance, strategy_used, started_at, finished_at, report_path
            FROM runs
            ORDER BY started_at DESC
            """
        ).fetchall()

