# RES Works Execution Backlog

This is the delivery ledger for the North Star. It is the planning authority
for grouped work; GitHub Issues may reference these story IDs, but an issue or
PR must not silently change their scope.

## How to read status

- **Complete** means implemented, tested, and merged.
- **In progress** means part of the capability exists, but its acceptance
  criteria are not complete.
- **Planned** means no production implementation is complete.

The current overall estimate is approximately **35–45%**. The foundation and
source-evidence pipeline are substantially built. Reliable architectural
reconciliation, documentation generation, Chief handoff, jurisdiction rules,
and end-to-end acceptance remain incomplete.

## Milestones

| ID | Milestone | Status | Estimate |
| --- | --- | --- | --- |
| M1 | Local runtime, API, database, and project lifecycle | Complete | 100% |
| M2 | Chief/CAPROJ/PDF/DXF/DWG intake and evidence bundle | In progress | 70% |
| M3 | Architectural extraction and cross-source reconciliation | In progress | 30% |
| M4 | Controlled notes, callouts, details, and recommendations | In progress | 50% |
| M5 | Designer approval and Chief handoff | In progress | 50% |
| M6 | Arkansas and local-jurisdiction validation | In progress | 40% |
| M7 | Final QA, watcher, and new-plan acceptance testing | Planned | 15% |

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
  orientation, layer, handle, and source snapshot.
- **M3.3** As a reviewer, I can compare full-floor and drawing-sheet exports.
  **Done:** differences in categories, dimensions, and source coverage become
  findings with severity and provenance.
- **M3.4** As a reviewer, I can reconcile CAD evidence with PDF pages.
  **Done:** findings link to a source file and PDF page where available;
  visual-only conclusions remain explicitly unverified.
- **M3.5** As a reviewer, I can inspect a usable plan preview. **Done:** the
  preview preserves scale/orientation and clearly labels unsupported geometry.

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
  item with decision history.
- **M5.2** As a designer, I can export an editable, sheet-targeted Chief
  handoff checklist and CAD/detail package. **In progress:** the handoff now
  carries approved item text, category, target sheet, and source references,
  and can render a human-editable checklist; file download and checkpoint
  recovery remain next in this milestone.
- **M5.3** As a designer, I can create a checkpoint and recover before any
  supervised write to Chief.

### M6 — Rules and jurisdiction

- **M6.1** As a reviewer, I can select project type, county, and municipality.
- **M6.2** As a reviewer, I can evaluate adopted baseline and local overlays
  with source, edition, and verification date.
- **M6.3** As a reviewer, I receive `pass`, `fail`, `not_verified`, or
  `professional_review_required`, never a guarantee of approval.

### M7 — Watcher and acceptance

- **M7.1** As a designer, a stable Chief export change starts one reproducible
  analysis run without duplicates.
- **M7.2** As a reviewer, Playwright covers upload, clear, analysis progress,
  evidence findings, and reopening the latest run.
- **M7.3** As a project owner, a new Lot 27 plan bundle passes the complete
  acceptance checklist with no mocked API responses.

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

## Next grouped delivery

Complete M3.2–M3.4 together: dimension normalization, full-floor versus
drawing-sheet comparison, PDF page links, conflict findings, and end-to-end
tests using the Lot 27 bundle.
