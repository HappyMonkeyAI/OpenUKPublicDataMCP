# OpenUKPublicDataMCP v1 Implementation Plan

> **For Hermes:** Use `subagent-driven-development` or `.agent-tasks.json` + coordination scripts for parallel lanes.

**Goal:** Ship a no-key-first, source-cited UK public-data MCP suitable for agent research briefs and DynamicMCPProxy mounting.

**Architecture:** Thin HTTP helpers (`http.py`), source registry (`sources.py`), cited envelopes + steering caps (`steering.py`), agent planning surface (`planning.py`), FastMCP tools in `server.py`. Optional-key providers behind env gates (ADR 0002).

**Tech stack:** Python 3.11+, FastMCP 2.x, httpx, pytest + respx.

**Baseline:** `docs/tests/Q2-executive-report.md` (smoke brief). DynamicMCPProxy patterns in `research/github-projects/dynamic-mcp-proxy-learnings.md`.

---

## Phase 0 — Done

| Task | Status |
|------|--------|
| Bootstrap package + tests | task-001 verified |
| Planning tools + steering + proxy catalogue entry | committed |
| Q2 executive test report | `docs/tests/Q2-executive-report.md` |

---

## Phase 1 — Core no-key sources (in progress)

### Task 1.1 — Environment Agency flood tools ✅ (this session)

- **Files:** `sources.py`, `server.py`, `tests/test_server.py`
- **Tools:** `list_flood_warnings`, `search_flood_areas`
- **Verify:** `pytest tests/test_server.py -k flood -v`

### Task 1.2 — ONS Beta API tools ✅ (this session)

- **Files:** `sources.py`, `server.py`, `tests/test_server.py`, `planning.py`
- **Tools:** `search_ons_datasets`, `get_ons_dataset`
- **Verify:** `pytest tests/test_server.py -k ons -v`
- **Follow-up:** `get_ons_latest_observations` (editions/versions path) — task extension

### Task 1.3 — Live smoke doc

- **Files:** `docs/tests/live-smoke-commands.md`
- **Content:** `fastmcp call` examples for flood + ONS + Q2-style brief
- **Verify:** manual or CI optional job

---

## Phase 2 — Architecture hygiene

### Task 2.1 — Thin source adapters

- **Create:** `src/openukpublicdata_mcp/adapters/ea_flood.py`, `adapters/ons.py`, `adapters/govuk.py`
- **Modify:** `server.py` — tools delegate to adapters only
- **Verify:** tests unchanged, `compileall`

### Task 2.2 — Optional-key provider pattern (task-004)

- **Create:** `docs/adr/0002-optional-key-providers.md`, `.env.example`
- **Pattern:** `COMPANIES_HOUSE_API_KEY` optional; tool returns structured `auth_required` envelope, never throws for missing key on list_sources

### Task 2.3 — Source priority catalogue (task-005)

- **Create:** `research/notes/source-priority-catalogue.md` from `co-cddo/api-catalogue` CSV mine

---

## Phase 3 — Agent / proxy integration

### Task 3.1 — Mount in DynamicMCPProxy

- Append `integrations/dynamic-mcp-proxy-user-catalogue-entry.json` to `~/projects/DynamicMCPProxy/user.catalogue.json`
- `proxy_handshake(tech_stack=["uk","python"], task_description="UK quarterly brief")`

### Task 3.2 — Regenerate Q2 brief with ONS tools

- Run `plan_uk_public_data_research` → `search_ons_datasets` → update `docs/tests/Q2-executive-report.md` appendix

---

## Phase 4 — Swarm execution (optional)

Use `.agent-tasks.json` + `scripts/tasks.py`:

```bash
AGENT_ID=codex-lane python3 scripts/tasks.py claim task-004
AGENT_ID=agy-lane python3 scripts/tasks.py claim task-005
```

Hermes orchestrates; verify with `verify-complete` after pytest.

---

## Verification gate (every phase)

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP
. .venv/bin/activate
pytest
python -m compileall src tests
fastmcp list src/openukpublicdata_mcp/server.py --json
```

Expected: all tests pass; **23+ tools** (MCP) + REST `/api/*` + `web/` explorer.

---

## Phase 5 — Web explorer ✅ (2026-07-05)

| Deliverable | Path |
|-------------|------|
| FastAPI bridge | `src/openukpublicdata_mcp/rest_api.py`, `openukpublicdata-web` |
| React + Leaflet UI | `web/` (search, topics, map drill-down, constituency via postcode) |
| Run script | `scripts/run-web.sh` |
| Tests | `tests/test_rest_api.py` |

Tier C (optional v2): EPC register, Met Office, Parliament API, full constituency GeoJSON boundaries.

---

## Out of scope (v1)

- Full ONS observations pagination
- Companies House / OS / TfL implementations (design only in ADR 0002)
- HTTP multi-tenant deployment
- ~~40mcp REST bridge~~ → shipped as `rest_api.py` + `web/`