"""Derive conservative observed facts from explicit plan geometry."""

from .models import FactKind, ObservedFact, PlanGeometry


def facts_from_geometry(plan: PlanGeometry, project_id: str) -> list[ObservedFact]:
    facts = [
        ObservedFact(
            id=f"{project_id}-project-type",
            key="project.type",
            value="residential",
            kind=FactKind.OBSERVED,
            source_ref=f"plan:{project_id}",
            confidence="medium",
        )
    ]
    for room in plan.rooms:
        if room.kind == "sleeping_room":
            facts.append(
                ObservedFact(
                    id=f"{project_id}-{room.id}-type",
                    key="room.type",
                    value="sleeping_room",
                    kind=FactKind.OBSERVED,
                    source_ref=f"plan:{project_id}/room/{room.id}",
                    confidence="high",
                )
            )
    for stair in plan.stairs:
        facts.extend(
            [
                ObservedFact(
                    id=f"{project_id}-{stair.id}-present",
                    key="stair.present",
                    value=True,
                    kind=FactKind.OBSERVED,
                    source_ref=f"plan:{project_id}/stair/{stair.id}",
                    confidence="high",
                ),
                ObservedFact(
                    id=f"{project_id}-{stair.id}-width",
                    key="stair.width",
                    value=stair.width,
                    kind=FactKind.OBSERVED,
                    source_ref=f"plan:{project_id}/stair/{stair.id}",
                    confidence="high",
                ),
            ]
        )
    return facts
