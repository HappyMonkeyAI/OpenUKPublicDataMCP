# Executive report 5 — Research & capability roadmap brief

**Audience:** Product, engineering, HappyMonkey / agent operators  
**Generated:** 5 July 2026 (UTC)  
**Purpose:** What OpenUKPublicDataMCP can do **today**, what needs keys, and what to build next

---

## Executive summary

The server exposes **19 MCP tools** across **10 registered sources** (`health_check` reports `source_count: 10`). **Seven sources are no-key-first** and power executive briefs 1–3. **Three optional-key** sources return structured `auth_required` without env vars. This document is the **capability map** for prioritising adapters, Hermes/DynamicMCPProxy mounting, and client-facing “UK public data agent” positioning.

---

## Server health (live)

| Field | Value |
|-------|--------|
| Status | ok |
| Server name | OpenUKPublicDataMCP |
| Source count | 10 |
| Retrieved | 2026-07-05T15:18:23Z |

**Tool:** `health_check`

---

## No-key core (Tier A) — production-ready

| Source ID | Tools | Executive use |
|-----------|-------|----------------|
| `govuk_search` | `search_govuk` | Releases, guidance, policy narrative |
| `data_gov_uk` | `search_public_datasets` | Open-data catalogue |
| `ons_beta_api` | `search_ons_datasets`, `get_ons_dataset`, `get_ons_latest_version`, `get_ons_observations` | Macro / inflation series |
| `carbon_intensity` | `get_carbon_intensity` | Live grid ops |
| `ea_flood_monitoring` | `list_flood_warnings`, `search_flood_areas` | Flood ops |
| `govuk_bank_holidays` | `get_bank_holidays` | Calendar / planning |
| `postcodes_io` | `lookup_postcode` | Geo anchor (community API) |

**Count:** 7 no-key sources (`list_sources(auth='none')` → **7** at retrieval).

**Agent planning:** `plan_uk_public_data_research`, `get_research_methodology`, `save_uk_research_note`

---

## Optional-key (Tier B) — wired, key-gated

| Source | Env vars | Tools |
|--------|----------|-------|
| Companies House | `COMPANIES_HOUSE_API_KEY` | `companies_house_company_profile` |
| Ordnance Survey Places | `OS_PLACES_API_KEY` | `os_places_find_place` |
| TfL Unified | `TFL_APP_ID`, `TFL_APP_KEY` | `tfl_line_status` |

Pattern: ADR **0002** — `auth_required` envelope when keys missing; no silent failure.

---

## Test artefacts (this directory)

| File | Template |
|------|----------|
| `Q2-executive-report.md` | Narrative Q2 2026 smoke + verified headlines |
| `exec-01-quarterly-uk-public-data-pulse.md` | Quarterly pulse (live MCP) |
| `exec-02-cost-of-living-inflation-snapshot.md` | Inflation / CPIH |
| `exec-03-climate-resilience-ops-brief.md` | Carbon + flood ops |
| `exec-05-research-capability-roadmap.md` | This document |
| `live-smoke-commands.md` | Operator command reference |

---

## Integration surfaces

| Surface | Status |
|---------|--------|
| FastMCP stdio | `uv run openukpublicdata-mcp` / `fastmcp call src/openukpublicdata_mcp/server.py …` |
| DynamicMCPProxy | Entry in `~/projects/DynamicMCPProxy/user.catalogue.json` (`openuk_public_data`) |
| Hermes `mcp_servers` | Add when you want native MCP (not only proxy) |
| Steering | `cap_envelope` truncates large payloads (e.g. bank holidays) |

**Catalogue detail:** `research/notes/source-priority-catalogue.md` (update Tier A ONS row to include observations tools).

---

## Backlog (Tier C — recommended next)

| Priority | Capability | Why |
|----------|------------|-----|
| P1 | ONS bulletin helper / CPI % from observations | Closer exec headlines without manual CSV |
| P1 | `planning.data.gov.uk` tools | National planning permissions (was research target) |
| P2 | Met Office DataPoint | Weather for resilience brief |
| P2 | Parliament / legislation read-only | Policy risk monitoring |
| P3 | Police.uk local crime aggregates | Place intelligence |
| P3 | Land Registry Price Paid | Property briefs |

---

## Swarm / task board

- Coordination: `AGENTS.md`, `.agent-tasks.json`, `scripts/tasks.py`, `scripts/lock.py`
- Completed tasks **001–007** (scaffold through ONS observations + optional-key wiring)
- Prompts: `.hermes/prompts/codex-task-006-*.md`, `agy-task-007-*.md`

---

## Reproduce capability audit

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP && . .venv/bin/activate
fastmcp list src/openukpublicdata_mcp/server.py
fastmcp call src/openukpublicdata_mcp/server.py health_check
fastmcp call src/openukpublicdata_mcp/server.py list_sources auth=none
pytest -q docs/tests/../..  # full suite: pytest -q from repo root
```

---

## Positioning line (external)

> “One MCP server, **no keys for core UK macro/energy/flood/discovery**, optional keys for **Companies House / OS / TfL**, every response **source-cited** for agent-safe executive summaries.”