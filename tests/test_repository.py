from pathlib import Path

from res_works.models import ApprovalStatus, DocumentationItem, ProjectManifest
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


def test_documentation_library_round_trips_controlled_item(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    item = DocumentationItem(
        id="note-existing-conditions",
        title="Existing conditions",
        text="Verify existing conditions in the field before construction.",
        category="general_note",
        source_ids=["internal-standard-001"],
        applies_when=["project.type=remodel"],
        revision="2",
        approval_status=ApprovalStatus.APPROVED,
        professional_review_required=True,
    )

    repository.save_documentation_item(item)

    assert repository.get_documentation_item(item.id) == item
    assert repository.list_documentation_items() == [item]
    repository.close()


def test_documentation_item_update_does_not_create_duplicate(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    first = DocumentationItem(
        id="callout-1", title="First", text="One", category="callout"
    )
    second = first.model_copy(update={"title": "Revised", "revision": "2"})

    repository.save_documentation_item(first)
    repository.save_documentation_item(second)

    items = repository.list_documentation_items()
    assert len(items) == 1
    assert items[0].title == "Revised"
    repository.close()
