# RES Works Documentation

This directory contains the product requirements and supporting technical and
operational documentation for RES Works.

## Requirements

- [Use cases and requirements](use-cases.md) - authoritative MVP behaviors,
  boundaries, and acceptance criteria.
- [North Star](north-star.md) - product goal, success definition, and decision
  test for implementation work.
- [Core processes](core-processes.md) - file watching, validation,
  recommendations, approval, and final QA workflow.
- [Arkansas residential code sources](arkansas-residential-code-sources.md) -
  statewide, Benton County, Washington County, and repository code-library
  source registry.
- [Execution plan](execution-plan.md) - product order, phases, deliverables,
  acceptance criteria, and first implementation sprint.
- [Execution backlog](execution-backlog.md) - grouped milestones, user
  stories, status estimates, acceptance criteria, and PR delivery rules.
- [Testing](testing.md) - local build, Docker smoke, Playwright, and real-file
  acceptance guidance.

The remaining implementation is grouped into five reviewable commits in the
execution plan, beginning with `.caproj` package intake and DXF/DWG geometry
evidence.

## Planned documents

- `architecture.md` - components, trust boundaries, data flow, and deployment
- `domain-model.md` - projects, conditions, notes, details, sources, and changes
- `chief-x18-integration.md` - templates, User Catalog, and macOS integration
- `note-authoring-standard.md` - IDs, printed text, metadata, and applicability
- `detail-authoring-standard.md` - CAD conventions and engineering boundaries
- `source-governance.md` - sources, verification, and jurisdiction overlays
- `security.md` - local permissions, MCP approvals, and file boundaries
- `testing.md` - fixtures, regression strategy, PDF QA, and MVP acceptance
- `operations.md` - installation, backup, update, and rollback
- `roadmap.md` - MVP sequence and post-MVP capabilities

## Documentation rules

- Use-case IDs are stable after publication.
- Requirements use **must**, recommendations use **should**, and optional
  behavior uses **may**.
- Printed construction-document content remains independent of municipal
  naming.
- Internal jurisdiction and source metadata remains traceable.
- Planned behavior is labeled as planned until an implementation and its tests
  exist.
