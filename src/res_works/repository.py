"""Small local SQLite repository for project state and review records."""

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import DocumentationItem, PdfPageEvidence, ProjectManifest, SourceSnapshot


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
