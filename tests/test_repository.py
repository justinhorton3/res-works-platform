from pathlib import Path

from res_works.models import ProjectManifest
from res_works.repository import ProjectRepository


def test_project_can_be_created_reopened_and_round_tripped(tmp_path: Path) -> None:
    database = tmp_path / "res-works.sqlite3"
    manifest = ProjectManifest(
        id="sweeter-build",
        name="Sweeter Build",
        address="Private project fixture",
        jurisdiction_profile_id="arkansas-baseline",
    )

    repository = ProjectRepository(database)
    repository.save_project(manifest)
    repository.close()

    reopened = ProjectRepository(database)
    assert reopened.get_project("sweeter-build") == manifest
    assert reopened.export_project("sweeter-build") == manifest.model_dump(mode="json")
    assert [item.id for item in reopened.list_projects()] == ["sweeter-build"]
    reopened.close()


def test_saving_same_project_updates_without_duplicates(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    repository.save_project(ProjectManifest(id="p-1", name="First"))
    repository.save_project(ProjectManifest(id="p-1", name="Updated"))

    projects = repository.list_projects()
    assert len(projects) == 1
    assert projects[0].name == "Updated"
    repository.close()


def test_missing_project_returns_none(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    assert repository.get_project("missing") is None
    assert repository.export_project("missing") is None
    repository.close()
