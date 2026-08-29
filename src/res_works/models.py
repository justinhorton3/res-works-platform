"""Typed, provider-independent domain models for the RES Works foundation."""

from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RESModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ConstraintLevel(StrEnum):
    MUST = "must"
    SHOULD = "should"
    NICE = "nice"


class ApprovalStatus(StrEnum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class FactKind(StrEnum):
    OBSERVED = "observed"
    CONFIRMED = "confirmed"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class CodeSource(RESModel):
    id: str
    title: str
    publisher: str
    edition: str | None = None
    jurisdiction: str
    url: str | None = None
    accessed_on: date | None = None
    licensed_content: bool = False


class RuleProfile(RESModel):
    id: str
    jurisdiction: str
    building_code: str
    sources: list[str] = Field(default_factory=list)
    status: Literal["draft", "verified", "needs_ahj_confirmation"] = "draft"


class Requirement(RESModel):
    id: str
    rule_profile_id: str
    title: str
    level: ConstraintLevel
    trigger: str
    requirement: str
    evidence_required: list[str] = Field(default_factory=list)
    source_id: str | None = None


class ValidationStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    NOT_VERIFIED = "not_verified"
    PROFESSIONAL_REVIEW_REQUIRED = "professional_review_required"


class ValidationResult(RESModel):
    requirement_id: str
    status: ValidationStatus
    message: str
    evidence_fact_ids: list[str] = Field(default_factory=list)
    source_id: str | None = None


class ValidationReport(RESModel):
    project_id: str
    rule_profile_id: str
    results: list[ValidationResult] = Field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for result in self.results:
            counts[result.status.value] = counts.get(result.status.value, 0) + 1
        return counts


class DocumentationItem(RESModel):
    id: str
    title: str
    text: str
    category: Literal["general_note", "callout", "cad_detail", "structural_detail"]
    source_ids: list[str] = Field(default_factory=list)
    applies_when: list[str] = Field(default_factory=list)
    revision: str = "1"
    verified_on: date | None = None
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    professional_review_required: bool = False


class ObservedFact(RESModel):
    id: str
    key: str
    value: str | float | int | bool | None
    kind: FactKind
    source_ref: str | None = None
    confidence: Literal["high", "medium", "low", "unknown"] = "unknown"


class SourceSnapshot(RESModel):
    id: str
    project_id: str
    filename: str
    media_type: str
    sha256: str
    byte_size: int
    page_count: int | None = None
    extracted_text: str | None = None


class EvidenceReference(RESModel):
    id: str
    snapshot_id: str
    locator: str
    description: str
    fact_ids: list[str] = Field(default_factory=list)


class PdfPageEvidence(RESModel):
    snapshot_id: str
    page_number: int
    text: str
    character_count: int
    has_text: bool


class PageRegion(RESModel):
    page_number: int
    x: float
    y: float
    width: float
    height: float
    label: str
    source: Literal["manual", "extracted", "inferred"] = "manual"


class Recommendation(RESModel):
    id: str
    project_id: str
    documentation_item_id: str
    reason: str
    evidence_fact_ids: list[str] = Field(default_factory=list)
    target_sheet: str | None = None
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    confidence: Literal["high", "medium", "low"] = "low"


class ChangeSet(RESModel):
    id: str
    project_id: str
    source_snapshot_id: str
    recommendation_ids: list[str] = Field(default_factory=list)
    version: int = 1
    status: Literal["draft", "submitted", "approved", "rejected"] = "draft"


class ProjectManifest(RESModel):
    id: str
    name: str
    address: str | None = None
    jurisdiction_profile_id: str | None = None
    chief_version: str = "X18"
    source_snapshot_ids: list[str] = Field(default_factory=list)
    documentation_item_ids: list[str] = Field(default_factory=list)
    created_on: date = Field(default_factory=date.today)
    schema_version: str = "0.1"


class Rect(RESModel):
    x: float
    y: float
    width: float = Field(gt=0)
    depth: float = Field(gt=0)

    @property
    def area(self) -> float:
        return self.width * self.depth

    def contains(self, other: "Rect") -> bool:
        return (
            other.x >= self.x
            and other.y >= self.y
            and other.x + other.width <= self.x + self.width
            and other.y + other.depth <= self.y + self.depth
        )

    def overlaps(self, other: "Rect") -> bool:
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.depth <= other.y
            or other.y + other.depth <= self.y
        )


class Room(RESModel):
    id: str
    name: str
    kind: str
    geometry: Rect


class Wall(RESModel):
    id: str
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    thickness: float = Field(gt=0)
    exterior: bool = False


class Opening(RESModel):
    id: str
    kind: Literal["door", "window"]
    wall_id: str
    offset: float = Field(ge=0)
    width: float = Field(gt=0)


class Stair(RESModel):
    id: str
    geometry: Rect
    width: float = Field(gt=0)
    riser: float | None = Field(default=None, gt=0)
    tread: float | None = Field(default=None, gt=0)


class PlanGeometry(RESModel):
    envelope: Rect
    rooms: list[Room] = Field(default_factory=list)
    walls: list[Wall] = Field(default_factory=list)
    openings: list[Opening] = Field(default_factory=list)
    stairs: list[Stair] = Field(default_factory=list)
    porches: list[Rect] = Field(default_factory=list)
