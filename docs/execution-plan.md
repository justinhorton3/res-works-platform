# RES Works Execution Plan

## North Star

Build a local, workflow-driven Chief Architect X18 documentation assistant
that turns a designer's native Chief model and exported permit set into a
traceable list of required notes, callouts, CAD details, structural details,
and review actions—while keeping Chief and the designer authoritative.

## Product order of operations

```text
Chief-native design
  -> controlled documentation library
  -> project evidence extraction
  -> applicable-content recommendations
  -> designer approval
  -> Chief-native placement/editing
  -> final Chief PDF
  -> supporting validation and QA
```

Validation is not the first product. It supports documentation completeness and
helps identify safety, code, and professional-review issues.

## What we need to build

### 1. Local project workspace

Deliverables:

- local project directory configuration;
- project manifest and version history;
- incoming Chief export folder;
- analysis-run folder;
- recommendations folder;
- approved-content folder; and
- archive and rollback records.

Acceptance:

- A project can be created, reopened, versioned, and archived locally.
- No data requires public hosting or external API access.

### 2. Chief X18 intake

Deliverables:

- import of a Chief project export/backup;
- PDF intake;
- DXF intake when supplied;
- schedule and reference-document intake;
- file stability checks;
- SHA-256 artifact hashing; and
- duplicate-run suppression.

Acceptance:

- A saved export creates one immutable analysis snapshot.
- Re-uploading the same artifact does not create a duplicate run.
- The original artifact is never modified.

### 3. Controlled documentation library

Deliverables:

- general notes;
- plan/detail callouts;
- editable CAD details;
- structural/construction details;
- schedule templates;
- sheet-content requirements;
- source records;
- applicability rules;
- revision history; and
- professional-review flags.

Acceptance:

- Every item has a neutral printed ID and controlled text.
- Every item has source, revision, verification date, applicability, and
  approval status.
- Printed content does not expose municipal metadata.

### 4. Project evidence model

Deliverables:

- observed facts;
- designer-confirmed facts;
- inferred facts;
- unknown values;
- source sheet/page/view references;
- confidence levels; and
- evidence links.

Acceptance:

- The system distinguishes observed, confirmed, inferred, and unknown facts.
- Safety, engineering, or permit-scope inferences require confirmation.

### 5. Documentation recommendation engine

Deliverables:

- map project conditions to library items;
- identify missing or incomplete documentation;
- generate recommended notes/details/callouts;
- identify target sheet/view;
- explain recommendation reason;
- show dependencies; and
- route unsupported conditions to professional review.

Acceptance:

- A review produces an actionable change list, not just a code list.
- Every recommendation includes evidence, source, reason, and confidence.
- Identical inputs and library versions produce identical recommendations.

### 6. Designer approval workflow

Deliverables:

- approve;
- edit instance;
- reject;
- defer;
- request clarification;
- group into change sets;
- preserve decision history; and
- create rollback checkpoints.

Acceptance:

- No Chief-writing action can run without explicit approval.
- Editing a project instance never changes the controlled library master.

### 7. Chief handoff outputs

Deliverables:

- editable CAD detail exports;
- note and callout insertion instructions;
- target sheet/view references;
- native-Chief placement checklist;
- future supervised automation boundary; and
- handoff log.

Acceptance:

- The designer can implement the approved change set in Chief without
  flattened-only output.
- The final layout remains editable in Chief.

### 8. Supporting validation and final QA

Deliverables:

- Arkansas statewide baseline profile;
- Benton County profile;
- Washington County profile;
- incorporated-city AHJ profiles;
- new-construction/remodel classification;
- geometry/document checks;
- sheet/content checks;
- evidence gaps;
- professional-review exceptions; and
- final-PDF comparison report.

Acceptance:

- Results are `pass`, `fail`, `not_applicable`, `not_verified`, or
  `professional_review_required`.
- The system never claims guaranteed permit approval.
- Unsupported checks are reported as unsupported rather than passed.

## Delivery phases

### Phase 0 — Repository and source foundation

Status: in progress

- establish repository structure;
- document North Star and core processes;
- document Arkansas code-source registry;
- define copyright-safe source strategy;
- select representative private fixtures; and
- define test and review conventions.

Exit criterion: requirements and source-governance documents are reviewed and
the first project fixture is authorized for private testing.

### Phase 1 — Documentation library and project model

Build first:

- typed Pydantic domain models;
- local SQLite repository;
- project manifest;
- `CodeSource`, `RuleProfile`, `Requirement`;
- `GeneralNote`, `Callout`, `CadDetail`, `StructuralDetail`;
- `ObservedFact`, `Recommendation`, `ChangeSet`; and
- unit tests for persistence and deterministic serialization.

Exit criterion: a project can store reusable content and generate a reviewable,
versioned change set from manually entered project facts.

### Phase 2 — Chief export and PDF review

Build next:

- local import endpoint/UI;
- artifact hashing and run tracking;
- PDF page inventory;
- text and visual evidence references;
- DXF layer/line inventory when available;
- changed-artifact watcher; and
- private regression PDF fixture workflow.

Exit criterion: an uploaded Chief export produces a reproducible evidence
snapshot and no duplicate processing on repeated hash.

### Phase 3 — Recommendation workflow

Build:

- applicability predicates;
- baseline content matching;
- county/AHJ overlays;
- missing-content findings;
- approval UI;
- change-set export; and
- decision history.

Exit criterion: the supplied permit set can produce a reviewable list of
general notes, callouts, CAD details, structural details, and unresolved
questions tied to source pages.

### Phase 4 — Chief-native handoff

Build:

- editable CAD output;
- native-Chief insertion checklist;
- sheet/view targeting;
- schedule and callout coordination;
- checkpoint and rollback records; and
- supervised automation research.

Exit criterion: an approved change set can be implemented in Chief without
flattening the final documentation or losing designer control.

### Phase 5 — Validation and final QA

Build:

- Arkansas baseline checks;
- Benton/Washington jurisdiction routing;
- municipal overlays;
- remodel rules;
- egress/life-safety checks;
- dimensional/document completeness checks;
- final-PDF regression reports; and
- professional-review routing.

Exit criterion: final Chief PDFs receive an evidence-backed exception report
with no silent unsupported checks.

## First implementation sprint

1. Create the typed documentation-library models.
2. Create SQLite tables and repository methods.
3. Add one original test library containing representative notes, callouts,
   and details.
4. Add a project manifest for a new residential project.
5. Add a manual-facts-to-recommendations service.
6. Add API tests for deterministic recommendations and approval states.
7. Add a minimal UI screen showing recommendations and approval actions.
8. Commit the complete vertical slice.

## Required inputs from the designer

- authorized private reference PDFs and Chief exports;
- preferred office general notes and detail library;
- preferred sheet naming and numbering convention;
- preferred callout format;
- project types to support first;
- AHJ/city list to prioritize; and
- decision on whether CAD details are authored in Chief CAD Detail format,
  DXF, or both.

Until those office standards are supplied, RES Works can build the data model,
workflow, source registry, and test harness, but it should not invent a final
office note library or claim that generated details are production-ready.

