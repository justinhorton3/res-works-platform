"""Small local SQLite repository for project state and review records."""

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import DocumentationItem, ProjectManifest, SourceSnapshot


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
