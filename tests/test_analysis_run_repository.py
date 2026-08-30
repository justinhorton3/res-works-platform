from pathlib import Path

from res_works.models import AnalysisRun
from res_works.repository import ProjectRepository


def test_analysis_runs_are_persisted_and_listed_by_project(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    run = AnalysisRun(
        id="run-001", project_id="sweeter-build", source_snapshot_ids=["snapshot-1"], result={"pages": 3}
    )
    repository.save_analysis_run(run)
    repository.save_analysis_run(run.model_copy(update={"status": "completed"}))

    assert repository.get_analysis_run("run-001").status == "completed"
    assert repository.get_analysis_run("run-001").result == {"pages": 3}
    assert repository.list_analysis_runs("sweeter-build") == [
        run.model_copy(update={"status": "completed"})
    ]
    assert repository.list_analysis_runs("other-project") == []
    repository.close()
