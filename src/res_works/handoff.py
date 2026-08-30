"""Approval-gated, native-Chief-safe handoff preparation."""

from hashlib import sha256
from html import escape

from .models import ApprovalDecision, ApprovalStatus, ChangeSet, ChiefHandoff, Recommendation


def apply_decisions(
    recommendations: list[Recommendation], decisions: list[ApprovalDecision]
) -> list[Recommendation]:
    """Return recommendation copies with explicit human decisions applied."""
    decision_map = {decision.recommendation_id: decision for decision in decisions}
    updated: list[Recommendation] = []
    for recommendation in recommendations:
        decision = decision_map.get(recommendation.id)
        if decision is None:
            updated.append(recommendation)
            continue
        status = {
            "approve": ApprovalStatus.APPROVED,
            "reject": ApprovalStatus.REJECTED,
            "defer": ApprovalStatus.DEFERRED,
            "request_clarification": ApprovalStatus.PROPOSED,
        }[decision.decision]
        updated.append(recommendation.model_copy(update={"status": status}))
    return updated


def build_change_set(
    project_id: str, source_snapshot_id: str, recommendations: list[Recommendation]
) -> ChangeSet:
    """Create a deterministic draft containing approved recommendations only."""
    approved_ids = sorted(
        recommendation.id
        for recommendation in recommendations
        if recommendation.status is ApprovalStatus.APPROVED
    )
    digest = sha256(
        f"{project_id}:{source_snapshot_id}:{','.join(approved_ids)}".encode()
    ).hexdigest()[:16]
    return ChangeSet(
        id=f"changeset-{digest}",
        project_id=project_id,
        source_snapshot_id=source_snapshot_id,
        recommendation_ids=approved_ids,
        status="draft",
    )


def build_chief_handoff(
    change_set: ChangeSet,
    chief_version: str = "X18",
    recommendations: list[Recommendation] | None = None,
) -> ChiefHandoff:
    """Prepare instructions for supervised Chief editing; never write native files."""
    return ChiefHandoff(
        project_id=change_set.project_id,
        change_set_id=change_set.id,
        source_snapshot_id=change_set.source_snapshot_id,
        chief_version=chief_version,
        recommendation_ids=change_set.recommendation_ids,
        items=[
            {
                "id": recommendation.id,
                "title": recommendation.title,
                "category": recommendation.category,
                "proposed_text": recommendation.proposed_text,
                "target_sheet": recommendation.target_sheet,
                "source_refs": recommendation.source_refs,
            }
            for recommendation in (recommendations or [])
            if recommendation.id in change_set.recommendation_ids
        ],
        instructions=[
            "Open the matching Chief project and verify the active plan view.",
            "Apply only the approved recommendation IDs listed in this handoff.",
            "Save a Chief checkpoint before editing and export a verification PDF afterward.",
        ],
    )


def render_handoff_markdown(handoff: ChiefHandoff) -> str:
    """Render a human-editable checklist for supervised Chief work."""
    lines = [
        "# RES Works — Chief Architect handoff", "",
        f"- Project: `{handoff.project_id}`",
        f"- Chief version: `{handoff.chief_version}`",
        f"- Change set: `{handoff.change_set_id}`",
        f"- Source snapshot: `{handoff.source_snapshot_id}`",
        "- Native file write performed: **No**", "", "## Preflight",
        *[f"- [ ] {instruction}" for instruction in handoff.instructions],
        "", "## Approved items",
    ]
    if not handoff.items:
        lines.append("- No recommendations approved for handoff.")
    for item in handoff.items:
        lines.extend(["", f"### {item['title']} (`{item['id']}`)",
            f"- Target sheet: {item.get('target_sheet') or 'Confirm in Chief'}",
            f"- Category: {item['category']}", f"- Proposed text: {item['proposed_text']}",
            f"- Evidence: {', '.join(item.get('source_refs') or []) or 'Confirm source evidence'}",
            "- [ ] Applied in Chief", "- [ ] Included in verification PDF"])
    return "\n".join(lines) + "\n"


def render_handoff_html(handoff: ChiefHandoff) -> str:
    """Render a browser-friendly handoff review without writing native files."""
    items = "".join(
        f"<article><h2>{escape(str(item['title']))}</h2><p><b>ID:</b> {escape(str(item['id']))}</p><p><b>Target:</b> {escape(str(item.get('target_sheet') or 'Confirm in Chief'))}</p><p>{escape(str(item['proposed_text']))}</p><p><b>Evidence:</b> {escape(', '.join(item.get('source_refs') or []) or 'Confirm source evidence')}</p><label>☐ Applied in Chief &nbsp; ☐ Included in verification PDF</label></article>"
        for item in handoff.items
    ) or "<p>No recommendations approved for handoff.</p>"
    instructions = "".join(f"<li>☐ {escape(instruction)}</li>" for instruction in handoff.instructions)
    return f"<!doctype html><html><head><meta charset=\"utf-8\"><title>RES Works Chief handoff</title><style>body{{font:16px system-ui;max-width:900px;margin:40px auto;color:#172033}}article{{border:1px solid #cbd5e1;border-radius:12px;padding:18px;margin:16px 0}}li{{margin:8px 0}}.notice{{background:#fff7ed;padding:14px;border-radius:10px}}</style></head><body><h1>RES Works — Chief Architect handoff</h1><p><b>Project:</b> {escape(handoff.project_id)}<br><b>Chief version:</b> {escape(handoff.chief_version)}<br><b>Change set:</b> {escape(handoff.change_set_id)}</p><div class=\"notice\"><b>Native file write performed: No.</b> Verify and apply items manually in Chief Architect.</div><h2>Preflight</h2><ul>{instructions}</ul><h2>Approved items</h2>{items}</body></html>"
