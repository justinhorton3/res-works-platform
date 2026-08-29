"""Page-level evidence extraction for reviewable PDF source documents."""

import hashlib
from pathlib import Path

from pypdf import PdfReader

from .models import PdfPageEvidence, SourceSnapshot


def inventory_pdf(path: str | Path, snapshot: SourceSnapshot) -> list[PdfPageEvidence]:
    pdf_path = Path(path)
    actual_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    if actual_hash != snapshot.sha256:
        raise ValueError("PDF does not match the source snapshot hash")
    pages = PdfReader(str(pdf_path)).pages
    evidence: list[PdfPageEvidence] = []
    for number, page in enumerate(pages, start=1):
        text = (page.extract_text() or "").strip()
        evidence.append(
            PdfPageEvidence(
                snapshot_id=snapshot.id,
                page_number=number,
                text=text,
                character_count=len(text),
                has_text=bool(text),
            )
        )
    return evidence
