# RES Works Platform

RES Works is a human-controlled residential permit-documentation assistant for
Chief Architect Premier X18 on macOS.

The platform lets a designer spend time on the creative parts of residential
design - walls, massing, rooms, roofs, openings, materials, and circulation -
while software assists with repetitive permit documentation.

Chief Architect remains the source of truth for the model, layout, notes,
details, schedules, revisions, and final PDF. RES Works recommends and prepares
content for the native Chief workflow; it does not replace Chief Architect or
silently publish construction documents.

## Project outcomes

RES Works will help a designer:

- determine which permit sheets are needed;
- select applicable reusable notes without printing municipal names or
  abbreviations on the sheets;
- recommend standard structural details and identify conditions requiring an
  Arkansas-licensed design professional;
- populate repetitive content in a native, editable X18 layout;
- review a Chief-exported permit set for missing information;
- retain hidden traceability from printed requirements to authoritative
  sources; and
- maintain complete human approval and editing control.

## Guiding principles

1. **Chief stays authoritative.** The final `.plan`, `.layout`, and PDF are
   created and controlled in Chief Architect X18.
2. **Human approval is required.** RES Works proposes document changes before
   native Chief content is inserted or changed.
3. **Printed content is neutral.** Printed note text and IDs use discipline
   identifiers such as `FND-008`, `FIRE-012`, and `DECK-014`. Municipal names,
   abbreviations, source URLs, and applicability metadata do not appear in the
   construction-document note.
4. **Requirements are traceable.** Every controlled note and detail retains
   source, applicability, verification date, revision, and status metadata.
5. **Engineering is not invented.** Non-prescriptive structural conditions are
   flagged for professional design rather than assigned unsupported values.
6. **Automation is reversible.** Native-document changes must be reviewable,
   logged, and recoverable from a known checkpoint.
7. **Deterministic logic precedes AI judgment.** Applicability, validation,
   identifiers, exports, and tests use deterministic software where possible.

## Initial scope

The MVP targets new detached one- and two-family residential projects in
Fayetteville, Springdale, Bella Vista, Bentonville, and Rogers, Arkansas.

Initial construction systems include conventional wood framing, manufactured
roof and floor systems, slabs, crawlspaces, basements, walkout basements,
attached garages, decks, covered porches, and common sloped-lot conditions.

Expansion to other Northwest Arkansas jurisdictions and project types will be
versioned after the MVP is validated.

## Getting started

The repository includes a local Docker Compose application for the intake and
review workflow. Native Chief editing remains supervised and local.

### Prerequisites

- macOS;
- Chief Architect Premier X18;
- Git;
- a local, non-iCloud working directory for active Chief files; and
- Codex or another MCP-capable development client for future local automation.

### Start the local application

From the repository root:

```bash
docker compose up --build
```

Open `http://localhost:5173/` for the review UI. The API health endpoint is
`http://localhost:8000/health`; Compose waits for it before starting the UI.
Stop the stack with `docker compose down`. Project data persists under the
local `storage/` directory and should not be committed.

Run the browser acceptance suite from `app/`:

```bash
npm run test:e2e
```

The browser suite uses deterministic test doubles for UI state transitions;
API and fixture tests provide the server-side validation path. A complete
real-file acceptance run still requires the operator's Lot 27 exports.

### Clone the repository

```bash
git clone https://github.com/justinhorton3/res-works-platform.git
cd res-works-platform
```

### Review the requirements

Start with:

- [Use cases and requirements](docs/use-cases.md)
- [Documentation index](docs/README.md)

All implementation work should reference one or more use-case IDs. A feature is
not complete merely because it runs; it must satisfy the applicable acceptance
criteria.

### Prepare Chief X18

Until the native templates are implemented:

1. Keep active `.plan`, `.layout`, referenced CAD, and generated files outside
   Desktop, Documents, or another iCloud-synchronized directory.
2. Export a backup of the X18 User Catalog before installing or updating RES
   Works content.
3. Use a copy of a project and layout while testing automation.
4. Do not grant macOS Accessibility control to an automation helper until its
   actions, permissions, and rollback behavior have been reviewed.

### Planned operator workflow

1. Create the architectural model in Chief X18.
2. Open the RES Works plan and layout templates.
3. Provide project conditions and the governing jurisdiction.
4. Export temporary review views or a review PDF from Chief.
5. Ask RES Works to analyze permit-document requirements.
6. Review, edit, approve, or reject the proposed change set.
7. Insert approved native notes, details, schedules, and linked views into the
   X18 layout.
8. Finish sheet composition directly in Chief.
9. Export the final permit PDF from Chief.
10. Run RES Works QA and resolve the reported exceptions.

Commands and installation steps will be added after the CLI and local MCP
server exist. Documentation must not present planned commands as available
functionality.

## Planned repository structure

```text
res-works-platform/
├── docs/                  # Requirements, decisions, workflows, and guides
├── schemas/               # Project and controlled-content schemas
├── standards/             # Notes, details, sources, and applicability rules
├── generators/            # Deterministic exports and detail generation
├── validators/            # Permit, source, and artifact validation
├── mcp/                   # Thin local MCP interface
├── macos/                 # Optional supervised X18 integration helper
├── tests/                 # Unit, integration, and regression tests
└── fixtures/              # Representative residential test projects
```

The MCP server will be an interface to tested application services, not the
location of core business rules.

## Safety and professional responsibility

RES Works is a documentation and quality-assurance system. It is not an
architect, structural engineer, surveyor, municipal reviewer, code official, or
licensed trade contractor. Project-specific zoning, covenants, site conditions,
code editions, local amendments, engineered systems, professional seals, and
AHJ interpretations require appropriate verification.

## Contributing

Before implementing a feature:

1. identify the governing use-case IDs;
2. update acceptance criteria when behavior changes;
3. preserve neutral printed IDs and hidden source metadata;
4. add deterministic tests for applicability and validation logic; and
5. document any action that can write to a Chief project or layout.

text-commit
