# RES Works Use Cases and Requirements

## 1. Purpose

This document defines the authoritative behavioral requirements for the RES
Works MVP.

The desired division of labor is simple: the designer creates and controls the
residential design and construction documents in Chief Architect Premier X18;
RES Works performs repetitive requirement selection, native-content
preparation, document-assembly assistance, traceability, and quality review.

## 2. Actors

| Actor | Responsibility |
| --- | --- |
| Designer | Creates the design, approves changes, controls the X18 layout, and exports the final PDF. |
| RES Works | Evaluates conditions, applies controlled rules, recommends content, and performs QA. |
| Standards maintainer | Authors and verifies notes, details, sources, mappings, and revisions. |
| Design professional | Supplies project-specific architectural or engineering design when required. |
| Authority having jurisdiction | Interprets and enforces applicable requirements. |

## 3. Priorities

- **P0** - required for a usable MVP.
- **P1** - required before broader production adoption.
- **P2** - valuable post-MVP enhancement.

## 4. Core use cases

### UC-001 - Configure a project

**Priority:** P0
**Actor:** Designer

The designer establishes the facts required to evaluate documentation needs.

**Requirements**

1. The system must record jurisdiction, project type, stories, areas,
   foundation, framing, garage, decks and porches, fuel, utilities, sprinklers,
   site conditions, and special conditions.
2. A value may be marked unknown.
3. User-confirmed facts must be distinguished from AI-inferred facts.
4. An inference affecting safety, engineering, or permit scope must require
   confirmation before becoming authoritative.
5. Project configuration must be versioned.

**Acceptance criteria**

- A manifest can be saved, reopened, validated, and compared with a prior
  version.
- Missing facts create actionable questions rather than invented values.

### UC-002 - Select the governing requirements profile

**Priority:** P0
**Actor:** Designer

The designer selects the project jurisdiction while RES Works applies the
strict office baseline and hidden local mapping.

**Requirements**

1. The MVP must support Fayetteville, Springdale, Bella Vista, Bentonville, and
   Rogers, Arkansas.
2. Municipal applicability must remain internal metadata.
3. Printed notes, printed code blocks, and printed callout IDs must not include
   municipal names or abbreviations.
4. Administrative requirements that do not belong on construction sheets must
   be routed to an internal submission checklist.
5. The designer must be able to inspect the source and last-verification date.

**Acceptance criteria**

- Changing jurisdiction changes applicable requirements without changing the
  neutral naming convention.
- Every selected requirement explains why it applies.

### UC-003 - Analyze a Chief project snapshot

**Priority:** P0
**Actor:** Designer

RES Works evaluates project conditions and omissions without changing the
native model.

**Requirements**

1. The system must accept a review PDF exported from Chief X18.
2. It should accept structured schedules and DXF exports when available.
3. Results must identify the sheets and views reviewed.
4. Uncertain observations must include confidence and request confirmation when
   they affect requirement selection.
5. Analysis must not modify the `.plan` or `.layout`.

**Acceptance criteria**

- Every result identifies its source sheet or view.
- Confirmed omissions are distinguished from items that cannot be verified.

### UC-004 - Determine the required sheet set

**Priority:** P0
**Actor:** RES Works

**Requirements**

1. Sheets must be selected from jurisdiction, project type, and construction
   conditions.
2. Each selected sheet must list required content and dependencies.
3. Optional and conditionally required sheets must be distinguishable.
4. Missing linked views must be reported rather than represented as complete.
5. The designer may add, retain, suppress, or reorder sheets.

**Acceptance criteria**

- Identical inputs and standards versions produce the same sheet proposal.
- Every automatically selected sheet has a traceable selection rule.

### UC-005 - Select controlled notes and callouts

**Priority:** P0
**Actor:** RES Works

**Requirements**

1. Each item must have a stable neutral ID, controlled printed text,
   discipline, applicability, exclusions, source, revision, lifecycle status,
   and verification date.
2. One canonical item must be used when jurisdictions share a requirement.
3. Conflicting items must block automatic approval.
4. The designer may approve, reject, defer, or edit a proposed instance.
5. Editing a project instance must not silently alter the controlled master.
6. Draft, obsolete, expired, or unverified items must not be automatically
   inserted into a production change set.

**Acceptance criteria**

- Every recommended item has an internal applicability explanation and source.
- Printed content contains no municipal metadata.
- Unchanged inputs produce the same selection.

### UC-006 - Select structural and construction details

**Priority:** P0
**Actor:** RES Works

**Requirements**

1. Details must have neutral IDs, titles, construction-system applicability,
   exclusions, sources, revisions, scales, and professional-review status.
2. The MVP must cover common foundation, framing, garage-separation, deck,
   porch, drainage, waterproofing, and envelope conditions.
3. Approved standard details must be available as editable CAD.
4. Conditions outside prescriptive limits must require project-specific
   professional design.
5. RES Works must not invent unsupported structural sizes, reinforcement,
   connections, or capacities.

**Acceptance criteria**

- Each recommendation states why it applies.
- Professional-design conditions appear in the exception list.
- Imported geometry and text remain editable in Chief.

### UC-007 - Create a proposed document change set

**Priority:** P0
**Actor:** RES Works

**Requirements**

1. Every proposed change must identify its sheet, action, content ID, reason,
   source, confidence, and dependencies.
2. Actions must distinguish insertion, replacement, removal, manual work, and
   professional-design work.
3. The designer may approve, edit, reject, or defer each action.
4. No Chief-writing action may run without approval.
5. Approved batches must have unique identifiers and timestamps.

**Acceptance criteria**

- The full change set can be reviewed before execution.
- Rejected and deferred actions remain in decision history.

### UC-008 - Populate a native Chief X18 layout

**Priority:** P0
**Actor:** Designer with RES Works assistance

**Requirements**

1. Chief X18 must remain authoritative for layout composition.
2. Notes must become editable native text or controlled library objects.
3. Details must become editable CAD rather than flattened images.
4. Plans, elevations, sections, and schedules should use linked native views
   where Chief supports them.
5. Every automation batch must begin from a saved checkpoint.
6. Integration must stop if the expected app, project, layout, or sheet is not
   active.
7. The designer must be able to reposition, edit, or delete inserted content.
8. The system must log what was inserted and where.

**Acceptance criteria**

- The resulting `.layout` remains editable in X18.
- No final permit sheet is substituted with a flattened RES Works PDF.
- A failed batch can be recovered from its checkpoint.

### UC-009 - Preserve designer control

**Priority:** P0
**Actor:** Designer

**Requirements**

1. The designer controls sheet order, layout-box crop, scale, placement,
   typography, content, and issue status.
2. An AI recommendation is never treated as approved solely because it was
   generated.
3. Normal Chief editing and export must remain possible without RES Works.
4. The authoritative final PDF must be exported from Chief X18.

**Acceptance criteria**

- Disabling MCP or the Mac helper does not prevent ordinary editing or export.

### UC-010 - Perform permit-document QA

**Priority:** P0
**Actor:** Designer

**Requirements**

1. QA must review the final candidate PDF exported from Chief.
2. It must evaluate sheet presence, expected content, cross-references,
   dimensions, labels, openings, egress, life safety, garages, decks,
   site/grading, and professional-design flags within supported scope.
3. Results must distinguish pass, fail, not applicable, not verified, and
   professional review required.
4. Every finding must identify a sheet and its evidence or missing evidence.
5. The system must not claim municipal approval or professional certification.

**Acceptance criteria**

- QA produces an exception-focused report with no silent unsupported checks.
- A clean report means no known exception within the implemented rule set; it
  does not guarantee approval.

### UC-011 - Manage resubmittals and revisions

**Priority:** P1
**Actor:** Designer

**Requirements**

1. Reviewer comments and their sources must be recorded.
2. Responses must identify affected sheets and content.
3. Revisions must use the normal change-set approval flow.
4. The system should generate a sheet-referenced resubmittal change list.
5. RES Works metadata must not replace Chief's native revision control.

**Acceptance criteria**

- Each comment is closed, deferred with explanation, or remains open.
- The change list reconciles with the approved revision batch.

### UC-012 - Maintain controlled standards content

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. Notes and details must support draft, verified, released, deprecated, and
   withdrawn states.
2. Identifiers must not be reused for different meanings.
3. Printed-text changes must create revisions.
4. Source and applicability changes must be reviewable as diffs.
5. Duplicate, conflicting, orphaned, and unsourced content must fail validation.
6. Released content must retain revision history.

**Acceptance criteria**

- A standards release can be reproduced from Git.
- Validation prevents unreleased content from entering production packages.

### UC-013 - Maintain jurisdiction and code sources

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. Sources must record authority, title, URL or file identity, effective date,
   retrieved date, and verification status.
2. Applicability must distinguish required, conditional, office-standard, and
   administrative status.
3. Sources exceeding their verification interval must be flagged.
4. A source update must not silently change released printed content.
5. Portal, naming, address-verification, and application rules must remain in
   submission workflows unless they affect construction content.

**Acceptance criteria**

- Every released item affected by a source change can be identified.
- Expired sources create warnings or release blockers according to policy.

### UC-014 - Install, update, back up, and roll back Chief content

**Priority:** P0
**Actor:** Designer

**Requirements**

1. Active Chief data and projects must remain outside synchronized cloud working
   directories.
2. Installation must require or verify a current User Catalog export.
3. Imports must be staged outside Chief's internal database folders.
4. Updates must be versioned and reversible.
5. RES Works must not directly edit Chief's internal catalog database.

**Acceptance criteria**

- The previous catalog and template version can be restored after a failed
  update.

### UC-015 - Operate through a local MCP interface

**Priority:** P1
**Actor:** Designer

**Requirements**

1. MCP must be a thin interface over tested application services.
2. Read, generate, approve, and Chief-write operations must be separate tools.
3. Chief-write tools require explicit approval.
4. Tools must be constrained to configured project and staging directories.
5. Tool results must be structured and auditable.
6. The deterministic CLI and validators must work without MCP.

**Acceptance criteria**

- Disabling MCP does not disable generation or validation.
- Tests verify tool permission and path boundaries.

### UC-016 - Perform supervised macOS integration

**Priority:** P1
**Actor:** Designer

**Requirements**

1. Automation must use stable app and menu state where possible and must not
   depend primarily on absolute screen coordinates.
2. Accessibility permission must be limited to the approved helper.
3. The helper must verify the active app, project, layout, and sheet.
4. It must stop on an unexpected dialog or state.
5. Actions must run in small approved batches with checkpoints and logs.
6. Manual placement must remain available when automation is unreliable.

**Acceptance criteria**

- An interrupted run does not corrupt the active project or catalog.
- The workflow can be completed manually with generated assets.

### UC-017 - Protect private project data

**Priority:** P0
**Actor:** Designer

**Requirements**

1. Local project files must not be uploaded without an explicit action and
   disclosed destination.
2. Secrets must not be stored in source control.
3. Logs must avoid unnecessary owner, address, credential, and signed-document
   content.
4. Temporary artifacts must have retention and cleanup rules.
5. Local-only processing must be supported for project artifacts.

**Acceptance criteria**

- A documented data-flow review identifies local and network operations.

### UC-018 - Create and maintain the Chief X18 plan template

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. The plan template must define approved Saved Plan Views, layer sets, default
   sets, annotation defaults, CAD layers, and reference-display behavior.
2. Template components must use stable names so generated recommendations can
   reference them deterministically.
3. Template releases must be versioned, backed up, and tested against the
   supported X18 release.
4. Updating the template must not silently alter existing projects.

**Acceptance criteria**

- A new project created from the template contains the documented views and
  defaults.
- The template version can be identified from the project documentation.

### UC-019 - Create and maintain the Chief X18 layout template

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. The layout template must provide the approved 24-by-36-inch border, title
   block, macros, sheet numbering, revision area, note zones, detail grids, and
   schedule zones.
2. Standard pages must define intended linked-view types, scales, and placement
   constraints without preventing designer editing.
3. Optional pages must remain identifiable without appearing in issued sets
   unless selected.
4. The template must not contain stale project or client information.

**Acceptance criteria**

- A new layout can be created without rebuilding standard sheet furniture.
- All template content remains editable in Chief X18.

### UC-020 - Package and maintain the Chief User Catalog

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. Released notes, callouts, details, symbols, and reusable components must be
   organized in a controlled RES Works catalog hierarchy.
2. Catalog releases must be exportable and installable using Chief-supported
   library workflows.
3. Catalog item names must map unambiguously to controlled content IDs and
   revisions.
4. Installation must not overwrite unrelated user content.
5. A previous catalog release must remain recoverable.

**Acceptance criteria**

- A clean X18 profile can import the released catalog and locate every item
  listed in its manifest.
- Catalog validation reports missing, duplicate, and revision-mismatched items.

### UC-021 - Author and publish editable CAD details

**Priority:** P0
**Actor:** Standards maintainer

**Requirements**

1. Detail sources must use controlled geometry, layers, line weights, fills,
   text sizes, scales, callouts, and revision metadata.
2. Each published detail must include an editable interchange artifact and a
   visual reference artifact.
3. Source, generated artifact, and Chief catalog versions must remain
   correlated.
4. Detail generation must be deterministic and visually regression-tested.
5. Professional-design placeholders must be visually distinct from completed
   prescriptive details.

**Acceptance criteria**

- The generated detail imports at the documented scale and remains editable.
- A rendered comparison detects unintended geometry or annotation changes.

### UC-022 - Assemble native note blocks and schedules

**Priority:** P0
**Actor:** RES Works

**Requirements**

1. Approved individual notes must be groupable into discipline and sheet note
   blocks without losing their controlled IDs.
2. Duplicate notes must collapse to one displayed instance unless repetition is
   explicitly required.
3. Block ordering and headings must follow controlled office rules.
4. Where Chief supports a native schedule, RES Works should prefer it over a
   flattened table.
5. Overflow must be detected before placement.

**Acceptance criteria**

- A note block can be regenerated from its manifest.
- The designer can edit placement and project-specific instances in Chief.

### UC-023 - Recommend and place linked views

**Priority:** P1
**Actor:** Designer with RES Works assistance

**Requirements**

1. RES Works must recommend the correct Saved Plan View, camera, section,
   elevation, or schedule for each selected sheet slot.
2. Recommendations must include intended scale, crop intent, and dependencies.
3. The system must not silently substitute an unlinked image when a native
   linked view is expected.
4. Existing designer-arranged views must be preserved unless their replacement
   is explicitly approved.

**Acceptance criteria**

- Every automated view placement is linked to the intended native view.
- Missing views are reported as actions rather than empty or misleading boxes.

### UC-024 - Adopt an existing Chief project

**Priority:** P1
**Actor:** Designer

**Requirements**

1. RES Works must assess an existing project for compatible views, layers,
   defaults, layout pages, and catalog content.
2. It must propose a migration plan before importing template settings.
3. Existing project-specific content must not be overwritten without approval.
4. The adoption workflow must support a backup and rollback point.

**Acceptance criteria**

- The designer can adopt RES Works incrementally without recreating the model.
- Conflicting names and defaults are disclosed before migration.

### UC-025 - Manage project-specific overrides

**Priority:** P1
**Actor:** Designer

**Requirements**

1. A project may override a note instance, detail selection, sheet decision, or
   applicability result with a recorded reason.
2. Overrides must be distinguishable from controlled standards changes.
3. Standards updates must not silently erase project overrides.
4. RES Works must warn when an override conflicts with a newly verified safety
   requirement.

**Acceptance criteria**

- The designer can list, review, retain, revise, or remove all active overrides.

### UC-026 - Generate calculations and project schedules

**Priority:** P1
**Actor:** Designer

**Requirements**

1. The system should reconcile conditioned, unconditioned, garage, porch, deck,
   footprint, and impervious areas from confirmed inputs.
2. It should produce opening, egress, deck-member, deferred-submittal, and
   inspection schedules where supported.
3. Calculated values must identify inputs, formula version, units, and rounding.
4. Unknown or conflicting inputs must prevent a false completed result.
5. Structural calculations requiring professional judgment are outside this
   use case.

**Acceptance criteria**

- Recalculation with unchanged inputs is deterministic.
- Schedule totals reconcile with the project manifest or report exceptions.

### UC-027 - Coordinate professional and deferred submittals

**Priority:** P0
**Actor:** Designer

**Requirements**

1. RES Works must identify conditions requiring an architect, engineer,
   surveyor, energy rater, truss designer, manufacturer, or licensed trade.
2. Each item must record responsible party, expected artifact, affected sheets,
   status, and due point.
3. Placeholder notes must not imply that missing professional design is
   complete.
4. Received documents must be checked for project, revision, and sheet
   coordination without altering professional seals.

**Acceptance criteria**

- The permit QA report lists every unresolved professional or deferred item.

### UC-028 - Prepare the jurisdiction submission package

**Priority:** P1
**Actor:** Designer

**Requirements**

1. RES Works must generate an internal checklist for required applications,
   supporting letters, worksheets, plan files, naming conventions, and portal
   steps.
2. Administrative requirements must remain separate from printed construction
   notes unless they affect construction.
3. File names and package contents must be validated against the selected
   jurisdiction profile.
4. Submission remains a user-controlled action.

**Acceptance criteria**

- The package report identifies present, missing, not applicable, and expired
  submission artifacts.
- RES Works does not upload or submit without explicit authorization.

### UC-029 - Assess a standards or code update

**Priority:** P1
**Actor:** Standards maintainer

**Requirements**

1. A changed source must produce an impact list of affected requirements,
   notes, details, templates, jurisdictions, and test fixtures.
2. Proposed changes must be reviewed before a new standards release.
3. Existing projects must retain their selected standards version unless the
   designer approves migration.
4. Superseded requirements must remain auditable.

**Acceptance criteria**

- A release comparison explains every controlled-content change and affected
  validation scenario.

### UC-030 - Add a jurisdiction profile

**Priority:** P2
**Actor:** Standards maintainer

**Requirements**

1. A new profile must define authoritative sources, applicability mappings,
   administrative requirements, verification interval, and test fixtures.
2. It must reuse canonical neutral content where possible.
3. Jurisdiction-specific duplication of printed notes must be reported.
4. A profile cannot be released until its required test scenario passes.

**Acceptance criteria**

- Adding a jurisdiction does not require changing printed IDs solely to encode
  municipal identity.

### UC-031 - Diagnose and recover an integration failure

**Priority:** P1
**Actor:** Designer

**Requirements**

1. RES Works must detect unavailable X18, missing templates, catalog mismatch,
   inaccessible paths, denied permissions, unexpected dialogs, and incomplete
   automation batches.
2. Error messages must describe completed actions, incomplete actions, and the
   safest recovery step.
3. Recovery must prefer the saved checkpoint and Chief-supported restore
   workflow.
4. Diagnostics must not expose credentials or unnecessary project content.

**Acceptance criteria**

- A simulated interruption produces a useful recovery report and leaves the
  original checkpoint intact.

### UC-032 - Audit system and document activity

**Priority:** P1
**Actor:** Designer or standards maintainer

**Requirements**

1. The system must record standards version, project-manifest version, analysis
   run, approved change set, placement batch, QA run, and catalog/template
   versions.
2. Audit records must distinguish human decisions from automated results.
3. Logs must be exportable for troubleshooting and reproducibility.
4. Retention must comply with the project-data protection requirements.

**Acceptance criteria**

- A user can reconstruct which inputs and approvals produced a candidate set.

## 5. Use-case coverage statement

The use cases above define the currently known end-to-end product scope. They
are expected to evolve through controlled requirement changes as Chief X18
integration is prototyped, municipal sources are verified, and test projects
expose missing workflows.

They are not a claim that every possible residential-design scenario has
already been discovered. New behavior must be added as a new use case or as an
explicit revision to an existing use case before implementation.

## 6. MVP content baseline

The MVP is expected to include at least:

- 75 released controlled notes;
- 25 released controlled callouts;
- 12 editable standard CAD details;
- one Chief X18 plan template;
- one Chief X18 24-by-36-inch layout template;
- one controlled User Catalog package;
- jurisdiction mappings for the five initial cities;
- slab, two-story deck, and sloped-walkout test fixtures; and
- automated schema, applicability, conflict, source, and PDF-QA tests.

Quantity alone does not establish completion. Content must satisfy lifecycle,
source, applicability, neutrality, and validation requirements.

## 7. MVP validation scenarios

### Scenario A - Simple slab residence

- Detached one-story dwelling
- Slab-on-grade
- Attached garage
- No elevated deck
- Municipal utilities

### Scenario B - Two-story residence with deck

- Engineered floor system and manufactured roof trusses
- Attached garage
- Elevated attached deck and exterior stairs

### Scenario C - Sloped walkout residence

- Walkout lower level and stepped foundation
- Attached garage at upper grade
- Deck or covered porch
- Retaining and concentrated-load conditions requiring professional review

Each scenario must produce a reproducible sheet, note, detail, submission, and
professional-review recommendation; preserve native Chief control; and provide
an exception-focused QA report from the Chief-exported candidate PDF.

## 8. Explicit MVP non-goals

The MVP will not:

- autonomously design or certify structural systems;
- apply a professional seal or guarantee permit approval;
- replace an AHJ, architect, engineer, surveyor, energy rater, or trade;
- create the authoritative final permit PDF outside Chief;
- modify architectural geometry;
- automate X18 through uncontrolled coordinate-based clicking;
- support every Northwest Arkansas jurisdiction or residential project type; or
- treat AI inference as confirmed project data.

## 9. Definition of success

The MVP succeeds when the designer can create the architectural model, approve
a traceable recommendation, receive editable native content in the Chief
layout, finish the document in X18, export the candidate PDF from Chief, and
receive a useful QA exception report.

It does not succeed if it merely generates an attractive external PDF or still
requires the designer to manually search the entire note and detail library for
every project.
