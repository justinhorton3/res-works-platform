# RES Works Core Processes

## 1. Operating model

Chief Architect remains the source of truth. RES Works observes project
artifacts, analyzes them locally, validates them against configured rules, and
prepares recommendations. It does not silently modify a Chief project or
claim that a project is approved.

The designer performs the primary architectural work in Chief X18. RES Works
supports the repeatable documentation workflow around that model by managing
controlled general notes, callouts, CAD details, structural details, sheet
requirements, and review decisions. Validation is a supporting process, not a
replacement for Chief's native modeling and documentation capabilities.

The core loop is:

```text
Chief edit
  -> saved/exported project artifact
  -> local watcher detects a stable change
  -> immutable analysis snapshot
  -> documentation-content analysis
  -> deterministic validation
  -> proposed notes/details/callouts/change set
  -> designer review and approval
  -> optional supervised Chief handoff
  -> Chief export
  -> final QA and exception report
```

## 1.1 Chief project package and derived exports

The preferred intake is a Chief Architect `.caproj` export. It is a ZIP-based
project package containing a manifest, native `.plan` and `.layout` files, and
resources. RES Works preserves the package as an immutable source record.

| Artifact | Role | Authority |
| --- | --- | --- |
| `.caproj` | Complete project package and provenance | Authoritative archive |
| `.plan` | Native architectural model | Chief source of truth |
| `.layout` | Native sheets and layout | Chief source of truth |
| `.dxf` / `.dwg` | Layer/entity/dimension geometry inspection | Derived analysis input |
| `.pdf` | Visual, sheet, note, and dimension review | Derived verification input |

The intake records the package manifest, contained files, sizes, hashes,
export errors, missing resources, and artifact relationships. Native files are
never edited by intake. A DXF/DWG discrepancy is a review finding, not
permission to rewrite the `.plan`.

## 2. File-watching workflow

### 2.1 Watched inputs

The first implementation should watch a RES Works project workspace containing
Chief exports and supporting files, such as:

- review PDFs;
- structured schedules;
- DXF exports when available;
- site, survey, and reference documents; and
- RES Works project manifests.

Native `.plan` and `.layout` files may be observed only when their file-change
behavior and safe-access rules are understood. They must not be treated as
editable inputs merely because the watcher can see them.

### 2.2 Change detection

The watcher must:

1. monitor only explicitly configured local project directories;
2. ignore temporary files, partial copies, caches, and generated outputs;
3. debounce rapid save events;
4. wait until the file size and modification time remain stable;
5. calculate a content hash;
6. create an artifact record with path, type, size, hash, timestamp, and
   originating project; and
7. start one reproducible analysis run for the changed artifact.

Repeated detection of the same hash must not create duplicate runs.

### 2.3 Run states

Each run should have an explicit state:

`detected` → `stabilizing` → `queued` → `analyzing` → `validated` →
`awaiting_review` → `approved` / `rejected` / `blocked`.

Failures must preserve the artifact, error, input hash, rule-set version, and
run identifier. A failed run must never be reported as complete.

## 3. Documentation-content workflow

RES Works should maintain reusable, versioned content libraries for:

- general notes;
- plan and detail callouts;
- editable CAD details;
- structural and construction details;
- schedules and standard sheet content; and
- source and applicability metadata.

The designer's Chief model supplies project conditions. RES Works maps those
conditions to candidate content, explains the match, and prepares an
approval-gated change set.

## 4. Validation pipeline

Validation is deterministic and precedes recommendations:

1. **Artifact integrity** — readable file, supported type, stable hash.
2. **Project facts** — jurisdiction, project type, construction conditions,
   and known/unknown values.
3. **Source coverage** — sheets/views/pages actually available for review.
4. **Geometry and document checks** — dimensions, labels, openings, rooms,
   stairs, garages, decks, and linked views within supported scope.
5. **Code/rule checks** — adopted IRC baseline and configured local overlays,
   with rule version and source recorded for every result.
6. **Professional review checks** — conditions outside prescriptive or
   supported boundaries become explicit exceptions.

Results must be classified as `pass`, `fail`, `not_applicable`,
`not_verified`, or `professional_review_required`.

## 5. Documentation recommendation process

After validation, RES Works evaluates what the permit set needs. A proposed
item may be:

- a controlled note;
- a callout;
- an editable CAD detail;
- a linked-view or schedule requirement;
- a manual Chief editing task; or
- a professional-design task.

Every recommendation must include its neutral content ID, reason, affected
sheet/view, evidence, source, standards revision, confidence, dependencies,
and approval state.

RES Works may prepare editable content from an approved standard. It must not
invent project-specific structural values, connections, capacities, or sealed
design. Those conditions are routed to professional review.

## 6. Human approval boundary

Automatic actions are limited to observation, analysis, validation, scoring,
rendering, and preparation of proposed content. Any action that writes to a
Chief project or layout requires:

1. a saved checkpoint;
2. a complete proposed change set;
3. designer approval;
4. an active-project and active-sheet check;
5. an action log; and
6. a recovery path.

Until a reliable supervised Chief integration exists, RES Works should export
editable intermediary files and instructions rather than pretend to automate
native Chief editing.

### Reviewer markup and amended PDF process

The reviewer works from rendered verification sheets. A note may be linked to a
page only, or may include coordinates for a visible point, arrow, or rectangle.
A missing item does not receive an artificial page mark unless the reviewer
deliberately adds one. The right-side notes rail is the working list; the source
PDF remains immutable.

When the reviewer requests an amended PDF, RES creates a new revision from the
source snapshot. Markups are painted onto copied sheet pages and a final
consolidated review page is appended. The revision stores the originating
`run_id`, source snapshot ID, annotation records, reviewer, and timestamp. A
review revision is evidence of requested changes, not proof of code compliance
or permit approval.

## 7. Final QA loop

The designer exports the candidate permit set from Chief. RES Works then:

1. records the final artifact hash;
2. identifies the sheets and views reviewed;
3. reruns supported checks;
4. compares findings with the prior run;
5. reports unresolved exceptions and newly introduced issues; and
6. records the final review decision.

A clean report means no known exception within the implemented rule set. It
does not guarantee jurisdictional approval, professional certification, or
construction suitability.

## 8. MVP implementation sequence

1. Project manifest and local workspace configuration.
2. Controlled content model for notes, callouts, CAD details, and structural details.
3. Chief export/snapshot intake with hash-based run tracking.
4. Content applicability and proposed change-set workflow.
5. Designer approval, revision history, and reusable project decisions.
6. Editable CAD/intermediary output and Chief insertion workflow.
7. Stable file watcher with duplicate-run suppression.
8. Validation, rule profiles, and final-PDF QA.
9. Supervised Chief handoff only after the safety boundary is tested.
