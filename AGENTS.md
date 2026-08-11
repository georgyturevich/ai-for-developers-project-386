## Agent skills

### Issue tracker

Issues live as GitHub issues in this repo, driven through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles map 1:1 to labels of the same name (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Project shape

Three packages, spec-first:

- **Repo root** — the API contract in TypeSpec (`main.tsp`), the single source of truth. `tsp-output/` (OpenAPI spec + bundled docs) is generated output — never hand-edit it; `make` regenerates it, and `npm run mock` serves a Prism mock of the spec on port 4010.
- **`frontend/`** — React + Vite UI that talks to the API only through generated types (`src/api/schema.d.ts`, gitignored). Its `typecheck`/`build` scripts recompile `main.tsp` first, so contract edits propagate automatically. Lint (`oxlint`), tests (Vitest) and typecheck all run inside `frontend/`.
- **`backend/`** — Python 3.14 FastAPI service (uv-managed) implementing the contract. Domain rules live in a framework-free core (`src/cal_bookings/domain.py`) with an injectable clock; data is an in-memory store (resets on restart, per the assignment); all errors use the contract's `code` + `message` body. Lint (`ruff`) and tests (`pytest`, including schemathesis conformance) run inside `backend/`; `make backend-test` regenerates the spec first. The server runs on port 8000 with CORS open for `http://localhost:5173`.
