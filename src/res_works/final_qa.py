"""Deterministic comparison and exception reporting for final Chief PDFs."""

from .models import PdfPageEvidence, ValidationReport, ValidationStatus


def compare_pdf_evidence(
    previous: list[PdfPageEvidence], current: list[PdfPageEvidence]
) -> dict[str, list[int]]:
    """Compare page text evidence without claiming visual equivalence."""
    before = {page.page_number: page.text for page in previous}
    after = {page.page_number: page.text for page in current}
    return {
        "added_pages": sorted(set(after) - set(before)),
        "removed_pages": sorted(set(before) - set(after)),
        "changed_pages": sorted(number for number in set(before) & set(after) if before[number] != after[number]),
    }


def unresolved_exceptions(report: ValidationReport) -> list[dict[str, str]]:
    """Return findings requiring action or additional evidence."""
    unresolved = {ValidationStatus.FAIL, ValidationStatus.NOT_VERIFIED, ValidationStatus.PROFESSIONAL_REVIEW_REQUIRED}
    return [
        {"requirement_id": result.requirement_id, "status": result.status.value, "message": result.message}
        for result in report.results
        if result.status in unresolved
    ]
