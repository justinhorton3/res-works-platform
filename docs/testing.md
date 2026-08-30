# Testing and local verification

RES Works uses layered checks:

1. `python3.12 -m pytest` runs domain and API regression tests.
2. `npm run build` verifies the Vue production bundle from `app/`.
3. `npm run test:e2e` runs the Playwright UI acceptance suite from `app/`.
4. `docker compose up --build` verifies the local service wiring; `/health`
   must return `{"status":"ok","service":"res-works-api"}`.

The Playwright UI tests intentionally mock network responses so that upload,
clear, failure, jurisdiction, and reopen states remain deterministic. They do
not replace real-bundle acceptance. For that, use a copy of the Lot 27 Chief
exports, keep them outside iCloud synchronization, upload the CAPROJ plus the
matching PLAN/LAYOUT/PDF/DXF exports, and confirm that the evidence bundle,
findings, and persisted run are visible.

No test may claim permit approval. Failures must retain the source artifact and
identify whether the problem occurred during upload, parsing, or validation.

The real-bundle integration test is `tests/test_real_bundle_acceptance.py`.
It creates a small valid CAPROJ container, PDF, and DXF and sends all three
through the real API analyzer. It verifies the combined evidence bundle,
parsed CAD entities, PDF pages, and native PLAN/LAYOUT provenance without
mocking the API.
