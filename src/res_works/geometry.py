"""Basic explicit geometry checks for residential plan layouts."""

from .models import PlanGeometry


def validate_geometry(plan: PlanGeometry) -> list[str]:
    errors: list[str] = []
    for room in plan.rooms:
        if not plan.envelope.contains(room.geometry):
            errors.append(f"room {room.id} extends outside the envelope")
    for index, room in enumerate(plan.rooms):
        for other in plan.rooms[index + 1 :]:
            if room.geometry.overlaps(other.geometry):
                errors.append(f"rooms {room.id} and {other.id} overlap")
    for stair in plan.stairs:
        if not plan.envelope.contains(stair.geometry):
            errors.append(f"stair {stair.id} extends outside the envelope")
        if stair.width < 4:
            errors.append(f"stair {stair.id} is narrower than 4 feet")
    return errors
