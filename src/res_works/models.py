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
