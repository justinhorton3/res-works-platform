# RES Works North Star

## North Star Goal

RES Works helps a residential designer move from a controlled project brief to
a complete, reviewable, traceable, and editable Chief Architect permit set —
with the designer and Chief Architect remaining authoritative at every step.

RES Works should make repetitive permit-documentation work faster and safer
without inventing design, engineering, code compliance, or approval. It must
turn project facts and verified standards into explainable recommendations,
approved change sets, and focused quality-assurance findings.

The primary product outcome is a repeatable Chief Architect X18 documentation
workflow. The designer performs the creative architectural work natively in
Chief—massing, walls, roofs, rooms, openings, stairs, materials, and
circulation—while RES Works prepares reusable construction-document content
around that model.

The validation and rules engine is secondary. It supports the workflow by
finding omissions, checking known conditions, and identifying professional
review items; it does not replace Chief's native modeling capabilities.

The authoritative intake package is a Chief Architect `.caproj` export. It
contains the native `.plan` and `.layout` files plus project resources. RES
Works preserves that package unchanged, uses DXF/DWG exports for geometry
inspection, and uses PDF exports for visual and sheet-level review.

## What success looks like

For a supported residential project, a designer can:

1. Create and edit the architectural model using native Chief X18 tools.
2. Reuse controlled general notes, callouts, CAD details, and structural details.
3. Record and version project facts, including unknowns.
4. Identify applicable requirements and explain why each applies.
5. Prepare a reviewable documentation change set around the model.
6. Approve, edit, reject, or defer every proposed change.
7. Export the authoritative final permit PDF from Chief Architect.
8. Run focused QA on that final export and resolve traceable exceptions.

The workflow preserves a complete chain from `.caproj` manifest to native
files, derived DXF/DWG and PDF snapshots, extracted evidence, approved
recommendations, and final Chief export.

## Non-negotiable boundaries

- Chief Architect remains the source of truth for the model, layout, and final PDF.
- Human approval is required before any native-document write.
- Deterministic rules come before AI judgment.
- Unsupported engineering and uncertain observations become explicit exceptions.
- Printed content remains jurisdiction-neutral; source and applicability metadata
  remain traceable internally.
- Automation is reversible, logged, and recoverable from a known checkpoint.
- Native Chief capabilities are preferred over duplicating design tools in RES Works.

## Product test

Every proposed feature should answer “yes” to these questions:

- Does it reduce repetitive documentation work for the designer?
- Does it preserve designer control and native Chief editability?
- Is its result deterministic, explainable, and testable?
- Can a reviewer trace the result to project facts, rules, and sources?
- Does it clearly expose uncertainty or professional-design responsibility?

If a feature cannot satisfy these tests, it is not North-Star-aligned for the project.
