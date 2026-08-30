"""Small local SQLite repository for project state and review records."""

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import (
    CodeSource,
    AnalysisRun,
    ApprovalDecision,
    HandoffCheckpoint,
    DocumentationItem,
    PdfPageEvidence,
    ProjectManifest,
    Requirement,
    RuleProfile,
    SourceSnapshot,
)


class ProjectRepository:
    """Persist RES Works records without requiring a server or hosted database."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                manifest_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS code_sources (
                id TEXT PRIMARY KEY, source_json TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS rule_profiles (
                id TEXT PRIMARY KEY, profile_json TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY, requirement_json TEXT NOT NULL
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS page_evidence (
                snapshot_id TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                evidence_json TEXT NOT NULL,
                PRIMARY KEY(snapshot_id, page_number)
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS source_snapshots (
                id TEXT PRIMARY KEY,
                snapshot_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS analysis_runs (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                run_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self._connection.execute("CREATE TABLE IF NOT EXISTS approval_decisions (recommendation_id TEXT PRIMARY KEY, decision_json TEXT NOT NULL)")
        self._connection.execute("CREATE TABLE IF NOT EXISTS approval_decision_history (id INTEGER PRIMARY KEY AUTOINCREMENT, recommendation_id TEXT NOT NULL, decision_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        self._connection.execute("CREATE TABLE IF NOT EXISTS handoff_checkpoints (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, checkpoint_json TEXT NOT NULL)")
        self._connection.execute(
            """CREATE TABLE IF NOT EXISTS documentation_items (
                id TEXT PRIMARY KEY,
                item_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def save_project(self, manifest: ProjectManifest) -> None:
        payload = manifest.model_dump(mode="json")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self._connection.execute(
            """INSERT INTO projects(id, manifest_json) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET
                manifest_json = excluded.manifest_json,
                updated_at = CURRENT_TIMESTAMP""",
            (manifest.id, encoded),
        )
        self._connection.commit()

    def get_project(self, project_id: str) -> ProjectManifest | None:
        row = self._connection.execute(
            "SELECT manifest_json FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row is None:
            return None
        return ProjectManifest.model_validate(json.loads(row["manifest_json"]))

    def list_projects(self) -> list[ProjectManifest]:
        rows = self._connection.execute(
            "SELECT manifest_json FROM projects ORDER BY id"
        ).fetchall()
        return [ProjectManifest.model_validate(json.loads(row["manifest_json"])) for row in rows]

    def export_project(self, project_id: str) -> dict[str, Any] | None:
        manifest = self.get_project(project_id)
        return manifest.model_dump(mode="json") if manifest else None

    def save_documentation_item(self, item: DocumentationItem) -> None:
        encoded = json.dumps(
            item.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        self._connection.execute(
            """INSERT INTO documentation_items(id, item_json) VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET
                item_json = excluded.item_json,
                updated_at = CURRENT_TIMESTAMP""",
            (item.id, encoded),
        )
        self._connection.commit()

    def get_documentation_item(self, item_id: str) -> DocumentationItem | None:
        row = self._connection.execute(
            "SELECT item_json FROM documentation_items WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            return None
        return DocumentationItem.model_validate(json.loads(row["item_json"]))

    def list_documentation_items(self) -> list[DocumentationItem]:
        rows = self._connection.execute(
            "SELECT item_json FROM documentation_items ORDER BY id"
        ).fetchall()
        return [
            DocumentationItem.model_validate(json.loads(row["item_json"]))
            for row in rows
        ]

    def save_snapshot(self, snapshot: SourceSnapshot) -> None:
        encoded = json.dumps(
            snapshot.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        self._connection.execute(
            "INSERT OR IGNORE INTO source_snapshots(id, snapshot_json) VALUES (?, ?)",
            (snapshot.id, encoded),
        )
        self._connection.commit()

    def get_snapshot(self, snapshot_id: str) -> SourceSnapshot | None:
        row = self._connection.execute(
            "SELECT snapshot_json FROM source_snapshots WHERE id = ?", (snapshot_id,)
        ).fetchone()
        return SourceSnapshot.model_validate(json.loads(row["snapshot_json"])) if row else None

    def list_snapshots(self, project_id: str) -> list[SourceSnapshot]:
        rows = self._connection.execute(
            "SELECT snapshot_json FROM source_snapshots WHERE json_extract(snapshot_json, '$.project_id') = ? ORDER BY rowid",
            (project_id,),
        ).fetchall()
        return [SourceSnapshot.model_validate(json.loads(row["snapshot_json"])) for row in rows]

    def delete_snapshot(self, snapshot_id: str) -> SourceSnapshot | None:
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot is None:
            return None
        self._connection.execute("DELETE FROM page_evidence WHERE snapshot_id = ?", (snapshot_id,))
        self._connection.execute("DELETE FROM source_snapshots WHERE id = ?", (snapshot_id,))
        self._connection.commit()
        return snapshot

    def save_analysis_run(self, run: AnalysisRun) -> None:
        encoded = json.dumps(run.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        self._connection.execute(
            """INSERT INTO analysis_runs(id, project_id, run_json) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET run_json = excluded.run_json""",
            (run.id, run.project_id, encoded),
        )
        self._connection.commit()

    def get_analysis_run(self, run_id: str) -> AnalysisRun | None:
        row = self._connection.execute(
            "SELECT run_json FROM analysis_runs WHERE id = ?", (run_id,)
        ).fetchone()
        return AnalysisRun.model_validate(json.loads(row["run_json"])) if row else None

    def list_analysis_runs(self, project_id: str) -> list[AnalysisRun]:
        rows = self._connection.execute(
            "SELECT run_json FROM analysis_runs WHERE project_id = ? ORDER BY created_at, id",
            (project_id,),
        ).fetchall()
        return [AnalysisRun.model_validate(json.loads(row["run_json"])) for row in rows]

    def save_approval_decision(self, decision: ApprovalDecision) -> None:
        self._connection.execute("INSERT INTO approval_decision_history(recommendation_id, decision_json) VALUES (?, ?)", (decision.recommendation_id, json.dumps(decision.model_dump(mode="json"), sort_keys=True)))
        self._connection.execute("INSERT INTO approval_decisions(recommendation_id, decision_json) VALUES (?, ?) ON CONFLICT(recommendation_id) DO UPDATE SET decision_json=excluded.decision_json", (decision.recommendation_id, json.dumps(decision.model_dump(mode="json"), sort_keys=True)))
        self._connection.commit()

    def list_approval_history(self, recommendation_id: str | None = None) -> list[ApprovalDecision]:
        if recommendation_id:
            rows = self._connection.execute("SELECT decision_json FROM approval_decision_history WHERE recommendation_id = ? ORDER BY id", (recommendation_id,)).fetchall()
        else:
            rows = self._connection.execute("SELECT decision_json FROM approval_decision_history ORDER BY id").fetchall()
        return [ApprovalDecision.model_validate(json.loads(row["decision_json"])) for row in rows]

    def list_approval_decisions(self) -> list[ApprovalDecision]:
        rows = self._connection.execute("SELECT decision_json FROM approval_decisions ORDER BY recommendation_id").fetchall()
        return [ApprovalDecision.model_validate(json.loads(row["decision_json"])) for row in rows]

    def save_checkpoint(self, checkpoint: HandoffCheckpoint) -> None:
        self._connection.execute("INSERT OR REPLACE INTO handoff_checkpoints(id, project_id, checkpoint_json) VALUES (?, ?, ?)", (checkpoint.id, checkpoint.project_id, json.dumps(checkpoint.model_dump(mode="json"), sort_keys=True)))
        self._connection.commit()

    def get_checkpoint(self, checkpoint_id: str) -> HandoffCheckpoint | None:
        row = self._connection.execute("SELECT checkpoint_json FROM handoff_checkpoints WHERE id = ?", (checkpoint_id,)).fetchone()
        return HandoffCheckpoint.model_validate(json.loads(row["checkpoint_json"])) if row else None

    def save_page_evidence(self, evidence: PdfPageEvidence) -> None:
        encoded = json.dumps(
            evidence.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        self._connection.execute(
            """INSERT INTO page_evidence(snapshot_id, page_number, evidence_json)
            VALUES (?, ?, ?)
            ON CONFLICT(snapshot_id, page_number) DO UPDATE SET
                evidence_json = excluded.evidence_json""",
            (evidence.snapshot_id, evidence.page_number, encoded),
        )
        self._connection.commit()

    def list_page_evidence(self, snapshot_id: str) -> list[PdfPageEvidence]:
        rows = self._connection.execute(
            """SELECT evidence_json FROM page_evidence
            WHERE snapshot_id = ? ORDER BY page_number""",
            (snapshot_id,),
        ).fetchall()
        return [PdfPageEvidence.model_validate(json.loads(row["evidence_json"])) for row in rows]

    def save_code_source(self, source: CodeSource) -> None:
        self._save_record("code_sources", source.id, source.model_dump(mode="json"))

    def get_code_source(self, source_id: str) -> CodeSource | None:
        value = self._get_record("code_sources", source_id)
        return CodeSource.model_validate(value) if value else None

    def save_rule_profile(self, profile: RuleProfile) -> None:
        self._save_record("rule_profiles", profile.id, profile.model_dump(mode="json"))

    def get_rule_profile(self, profile_id: str) -> RuleProfile | None:
        value = self._get_record("rule_profiles", profile_id)
        return RuleProfile.model_validate(value) if value else None

    def save_requirement(self, requirement: Requirement) -> None:
        self._save_record("requirements", requirement.id, requirement.model_dump(mode="json"))

    def get_requirement(self, requirement_id: str) -> Requirement | None:
        value = self._get_record("requirements", requirement_id)
        return Requirement.model_validate(value) if value else None

    def _save_record(self, table: str, record_id: str, value: dict[str, Any]) -> None:
        columns = {
            "code_sources": "source_json",
            "rule_profiles": "profile_json",
            "requirements": "requirement_json",
        }
        column = columns[table]
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
        self._connection.execute(
            f"INSERT INTO {table}(id, {column}) VALUES (?, ?) "
            f"ON CONFLICT(id) DO UPDATE SET {column} = excluded.{column}",
            (record_id, encoded),
        )
        self._connection.commit()

    def _get_record(self, table: str, record_id: str) -> dict[str, Any] | None:
        column = {
            "code_sources": "source_json",
            "rule_profiles": "profile_json",
            "requirements": "requirement_json",
        }[table]
        row = self._connection.execute(
            f"SELECT {column} FROM {table} WHERE id = ?", (record_id,)
        ).fetchone()
        return json.loads(row[column]) if row else None
