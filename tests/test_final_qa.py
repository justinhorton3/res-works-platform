from res_works.final_qa import compare_pdf_evidence, unresolved_exceptions
from res_works.models import PdfPageEvidence, ValidationReport, ValidationResult, ValidationStatus


def page(number: int, text: str) -> PdfPageEvidence:
    return PdfPageEvidence(snapshot_id="snapshot", page_number=number, text=text, character_count=len(text), has_text=bool(text))


def test_pdf_comparison_reports_page_changes() -> None:
    assert compare_pdf_evidence([page(1, "old"), page(2, "same")], [page(1, "new"), page(3, "added")]) == {
        "added_pages": [3], "removed_pages": [2], "changed_pages": [1]
    }


def test_unresolved_exceptions_excludes_passes() -> None:
    report = ValidationReport(project_id="p", rule_profile_id="r", results=[
        ValidationResult(requirement_id="ok", status=ValidationStatus.PASS, message="ok"),
        ValidationResult(requirement_id="missing", status=ValidationStatus.NOT_VERIFIED, message="needs evidence"),
    ])
    assert unresolved_exceptions(report) == [{"requirement_id": "missing", "status": "not_verified", "message": "needs evidence"}]
