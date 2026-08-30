"""Deterministic evidence-to-documentation recommendation matching."""

import hashlib
from collections.abc import Iterable

from .models import DocumentationItem, ObservedFact, Recommendation


def _matches(expression: str, facts: list[ObservedFact]) -> bool:
    key, separator, expected = expression.partition("=")
    if not separator:
        return False
    return any(fact.key == key and str(fact.value) == expected for fact in facts)


def recommend_documentation(
    project_id: str,
    items: Iterable[DocumentationItem],
    facts: Iterable[ObservedFact],
) -> list[Recommendation]:
    available = list(facts)
    recommendations: list[Recommendation] = []
    for item in items:
        if not item.applies_when or not all(_matches(condition, available) for condition in item.applies_when):
            continue
        evidence = [fact for fact in available if fact.key in {condition.split("=", 1)[0] for condition in item.applies_when}]
        source_refs = sorted({fact.source_ref for fact in evidence if fact.source_ref})
        target_sheet = {
            "general_note": "General Notes",
            "callout": "Plan / Callouts",
            "cad_detail": "CAD Details",
            "structural_detail": "Structural Details",
        }[item.category]
        seed = f"{project_id}:{item.id}:{item.revision}".encode()
        recommendation_id = hashlib.sha256(seed).hexdigest()[:16]
        recommendations.append(
            Recommendation(
                id=f"rec-{recommendation_id}",
                project_id=project_id,
                documentation_item_id=item.id,
                title=item.title,
                category=item.category,
                proposed_text=item.text,
                reason=f"Matched applicability conditions for {item.title}.",
                evidence_fact_ids=[fact.id for fact in evidence],
                source_refs=source_refs,
                target_sheet=target_sheet,
                professional_review_required=item.professional_review_required,
                confidence="high" if all(fact.confidence == "high" for fact in evidence) else "medium",
            )
        )
    return recommendations
