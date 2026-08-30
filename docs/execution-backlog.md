# RES Works Execution Backlog

This is the delivery ledger for the North Star. It is the planning authority
for grouped work; GitHub Issues may reference these story IDs, but an issue or
PR must not silently change their scope.

## How to read status

- **Complete** means implemented, tested, and merged.
- **In progress** means part of the capability exists, but its acceptance
  criteria are not complete.
- **Planned** means no production implementation is complete.

The current overall estimate is approximately **88%** by story-weighted scope
(updated 2026-08-30). This is an implementation-progress measure, not a claim
that any plan is permit-ready.

## Milestones

| ID | Milestone | Status | Estimate |
| --- | --- | --- | --- |
| M1 | Local runtime, API, database, and project lifecycle | Complete | 100% |
| M2 | Chief/CAPROJ/PDF/DXF/DWG intake and evidence bundle | Complete | 100% |
| M3 | Architectural extraction and cross-source reconciliation | Complete | 100% |
| M4 | Controlled notes, callouts, details, and recommendations | Complete | 100% |
| M5 | Designer approval and Chief handoff | Complete | 100% |
| M6 | Arkansas and local-jurisdiction validation | Complete | 100% |
| M7 | Final QA, watcher, and new-plan acceptance testing | Complete | 100% |
| M8 | Operational hardening | Complete | 100% |
| M9 | Real-bundle integration | Complete | 100% |
| M10 | Reproducible test runtime | Complete | 100% |
| M11 | Reviewer markup and amended review PDF | In progress | 75% |

## User stories and acceptance criteria

### M1 — Runtime and lifecycle

- **M1.1** As a designer, I can start the UI, API, and database together with
  Docker Compose. **Done:** health endpoint, persistent local storage, and
  documented startup commands pass a smoke test.
- **M1.2** As a designer, I can upload, reopen, hash, and remove project
  artifacts. **Done:** records persist, duplicate hashes are controlled, and
  delete clears stored evidence.

### M2 — Source intake and evidence

- **M2.1** As a designer, I can upload CAPROJ and see native PLAN/LAYOUT
  members. **Done:** archive paths, sizes, manifest metadata, and resource
  warnings are visible.
- **M2.2** As a designer, I can associate PDF, DXF, and DWG exports with the
  same project. **Done:** one analysis run reports every source snapshot.
- **M2.3** As a reviewer, I can see what each source can prove. **Done:** the
  UI distinguishes available, missing, unsupported, and visual-review-only
  evidence.
- **M2.4** As a designer, I can clear an incorrect evidence bundle. **Done:**
  server records, page evidence, extracted files, and UI state are cleared.

### M3 — Architectural extraction and reconciliation

- **M3.1** As a reviewer, I can see DXF counts for walls, doors, windows,
  stairs, cabinets, plumbing, fireplaces, and room labels.
- **M3.2** As a reviewer, I can inspect DXF dimensions with value, units,
  orientation, layer, handle, and source snapshot. **Done:** normalized
  dimension evidence retains source identity and handles.
- **M3.3** As a reviewer, I can compare full-floor and drawing-sheet exports.
  **Done:** repeated and unmatched normalized dimensions are reported with
  source provenance and conservative review severity.
- **M3.4** As a reviewer, I can reconcile CAD evidence with PDF pages.
  **Done:** indexed PDF page references are returned with snapshot identity;
  visual-only conclusions remain explicitly unverified.
- **M3.5** As a reviewer, I can inspect a usable plan preview. **Done:** the
  SVG preserves source aspect ratio, coordinates, units metadata, and source
  layer/handle titles for traceable linework.

### M4 — Documentation intelligence

- **M4.1** As a designer, I can maintain versioned general notes, callouts,
  CAD details, structural details, and schedules.
- **M4.2** As a reviewer, I receive recommendations tied to observed facts,
  source evidence, target sheet/view, proposed text, category, reason,
  confidence, and review status. **Done:** each recommendation is actionable
  in the UI and preserves source references and professional-review flags.
- **M4.3** As a designer, I can distinguish missing documentation from a code
  failure. **Done:** recommendations never claim permit approval.

### M5 — Approval and Chief handoff

- **M5.1** As a designer, I can approve, edit, defer, or reject each proposed
  item with decision history. **Done:** latest state and append-only decision
  history are persisted and queryable.
- **M5.2** As a designer, I can export an editable, sheet-targeted Chief
  handoff checklist and CAD/detail package. **Done:** approved item text,
  category, target sheet, source references, and a downloadable Markdown
  checklist are produced without modifying native Chief files.
- **M5.3** As a designer, I can create a checkpoint and recover before any
  supervised write to Chief. **Done:** checkpoint creation and recovery are
  explicit API operations and native writes remain prohibited.

### M6 — Rules and jurisdiction

- **M6.1** As a reviewer, I can select project type, county, and municipality.
  **Done:** the selector and validation API route classification through the
  selected profile.
- **M6.2** As a reviewer, I can evaluate adopted baseline and local overlays
  with source, edition, and verification date. **Done:** profile scope exposes
  source IDs, inherited county overlays, and explicit verification state;
  pending AHJ confirmation remains visible.
- **M6.3** As a reviewer, I receive `pass`, `fail`, `not_verified`, or
  `professional_review_required`, never a guarantee of approval. **Done:**
  validation returns evidence-backed statuses plus a mandatory AHJ notice.

### M7 — Watcher and acceptance

- **M7.1** As a designer, a stable Chief export change starts one reproducible
  analysis run without duplicates. **Done:** deterministic stable-change
  detection, hash-backed polling, bounded watch loops, and API dispatch are
  implemented.
- **M7.2** As a reviewer, Playwright covers upload, clear, jurisdiction status,
  analysis progress, evidence findings, failure visibility, and reopening the
  latest run. **Done:** the six-state UI acceptance suite passes.
- **M7.3** As a project owner, a new Lot 27 plan bundle passes the complete
  acceptance checklist with no mocked API responses. **Done:** the Docker test
  profile runs the real CAPROJ/PDF/DXF bundle acceptance test.

### M8 — Operational hardening

- **M8.1** As an operator, I can start the local stack with health-checked
  service dependencies and documented smoke commands.
- **M8.2** As a developer, I can distinguish deterministic UI tests from
  real-file/API acceptance and know what remains to verify with Lot 27 exports.

M8 is complete when Compose healthchecks, startup documentation, build checks,
and the real-bundle acceptance procedure are present. It does not imply that
the current implementation is permit-ready.

### M9 — Real-bundle integration

- **M9.1** As a project owner, I can analyze CAPROJ, PDF, and DXF evidence
  together through the API and verify native PLAN/LAYOUT provenance.
- **M9.2** As a reviewer, I can use a repeatable no-mock Lot 27 bundle test
  before accepting a release.

M9 is complete when the real-bundle test runs in the supported Python/Docker
  environment and the operator verifies the supplied Lot 27 exports.

### M10 — Reproducible test runtime

- **M10.1** As a developer, I can run the complete Python suite in the same
  supported Python 3.12 family as the API without host dependency drift.
- **M10.2** As a project owner, I can run the real-bundle acceptance test from
  Docker and retain its output as release evidence.

M10 is complete when the test profile builds, runs, and reports the suite
  independently of the runtime API image.

### M11 - Reviewer markup and amended review PDF

- **M11.1** As a reviewer, I can review sheets at a readable scale with a
  right-side notes rail and continuous page scrolling. **Done:** the viewer
  supports full-screen sheet review, zoom, page-specific notes, and persisted
  run-scoped annotations.
- **M11.2** As a reviewer, I can mark a specific plan location with an optional
  note, arrow, or rectangle. **In progress:** note pins and coordinates exist;
  arrow and rectangle editing remain to be completed.
- **M11.3** As a reviewer, I can generate an amended PDF without changing the
  original source. **In progress:** bake persisted markups onto copied PDF
  pages and append a consolidated review page; immutable revision metadata and
  visual output verification remain.
- **M11.4** As a reviewer, I can append a consolidated review page listing all
  required changes, page references, statuses, and notes. **Planned:** render
  the appendix into the amended PDF and retain its generation metadata.

M11 is complete when annotations persist by run and page, amended PDFs render
without clipping, the original source remains unchanged, and the appended
review page reconciles every open item.

## Grouped PR policy

One PR should complete a coherent milestone or vertical slice, including its
tests and UI/API changes. Documentation-only PRs are reserved for changes to
the delivery contract or source governance. Do not split a single user story
into separate PRs for model, endpoint, and label changes unless a dependency
or safety boundary requires it.

## Definition of done

A story is complete only when implementation, tests, UI behavior, source
provenance, failure state, documentation, and review instructions are all
present. A build that merely displays an inventory is not evidence that the
underlying architectural analysis is complete.

## Post-milestone operational work

The implementation milestones are complete. The owner must verify current code
editions and local amendments with each AHJ before relying on a profile for a
real permit submission.
