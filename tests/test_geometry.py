from res_works.geometry import validate_geometry
from res_works.models import PlanGeometry, Rect, Room, Stair


def test_valid_explicit_geometry_has_no_errors() -> None:
    plan = PlanGeometry(
        envelope=Rect(x=0, y=0, width=30, depth=54),
        rooms=[Room(id="living", name="Living", kind="living_room", geometry=Rect(x=0, y=0, width=15, depth=20))],
        stairs=[Stair(id="main", geometry=Rect(x=15, y=0, width=4, depth=12), width=4)],
    )
    assert validate_geometry(plan) == []


def test_geometry_rejects_overlap_and_outside_rooms() -> None:
    plan = PlanGeometry(
        envelope=Rect(x=0, y=0, width=30, depth=30),
        rooms=[
            Room(id="a", name="A", kind="bedroom", geometry=Rect(x=0, y=0, width=10, depth=10)),
            Room(id="b", name="B", kind="bath", geometry=Rect(x=5, y=5, width=10, depth=10)),
            Room(id="c", name="C", kind="office", geometry=Rect(x=25, y=25, width=10, depth=10)),
        ],
    )
    errors = validate_geometry(plan)
    assert "rooms a and b overlap" in errors
    assert "room c extends outside the envelope" in errors


def test_geometry_rejects_stair_under_four_feet() -> None:
    plan = PlanGeometry(
        envelope=Rect(x=0, y=0, width=30, depth=30),
        stairs=[Stair(id="main", geometry=Rect(x=0, y=0, width=3.5, depth=12), width=3.5)],
    )
    assert validate_geometry(plan) == ["stair main is narrower than 4 feet"]
