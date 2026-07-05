# OpenUKPublicDataMCP

OpenUKPublicDataMCP is a no-key-first Model Context Protocol server for useful UK public data.

The goal is to give Claude, Hermes, Cursor, and other MCP clients one reliable endpoint for common UK public-data questions: postcodes, GOV.UK content, bank holidays, carbon intensity, public datasets, flood monitoring, parliamentary/legal/statistical lookups, and optional-key enrichments such as Companies House, EPC, Ordnance Survey, and TfL.

## Status

MVP shipped: **23+ MCP tools**, FastAPI explorer API, and **`web/`** React map UI. Tier C backlog (EPC, Met Office, Parliament) remains optional.

## Principles

- No-key-first: core tools must work without signup.
- Source-cited: every tool returns upstream source metadata and retrieval time.
- Official-first: prefer official UK public sector APIs; label community/non-official sources explicitly.
- Thin adapters: normalize useful fields but keep upstream payloads available.
- Optional enrichments: API-key sources are allowed only as optional modules.
- Read-only by default: no public-sector write operations in the initial project.

## Current tools

- `health_check` — server health and configured source count.
- `list_sources` — source registry with auth/licence/freshness notes.
- `plan_uk_public_data_research` / `get_research_methodology` / `save_uk_research_note` — agent planning surface.
- `lookup_postcode` — postcode lookup via postcodes.io.
- `get_bank_holidays` — GOV.UK bank holidays by UK region.
- `get_carbon_intensity` — National Grid ESO carbon intensity for Great Britain.
- `search_govuk` — GOV.UK Search API.
- `search_public_datasets` — data.gov.uk CKAN package search.
- `list_flood_warnings` / `search_flood_areas` — Environment Agency flood monitoring (England).
- `search_ons_datasets` / `get_ons_dataset` / `get_ons_latest_version` / `get_ons_observations` — ONS Beta API.
- `search_planning_applications` — planning.data.gov.uk (England).
- `get_cpih_inflation_headline` — CPIH month-on-month % from ONS observations.
- `list_uk_regions` — explorer geography metadata (sample postcodes).
- `police_street_crime_near` — data.police.uk near lat/lng.
- `search_mp_by_postcode`, `search_constituencies` — UK Parliament Members API.
- `met_office_site_forecast` — Met Office DataHub (optional `MET_OFFICE_DATAHUB_API_KEY`).
- `companies_house_company_profile` — optional `COMPANIES_HOUSE_API_KEY`.
- `os_places_find_place` — optional `OS_PLACES_API_KEY`.
- `tfl_line_status` — optional `TFL_APP_ID` + `TFL_APP_KEY`.

Implementation plan: `docs/plans/2026-07-05-openuk-v1-implementation.md`. Test brief: `docs/tests/Q2-executive-report.md`.

## Quick start

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python -m openukpublicdata_mcp.server
```

Run validation:

```bash
pytest
fastmcp inspect src/openukpublicdata_mcp/server.py:mcp
fastmcp list src/openukpublicdata_mcp/server.py --json
fastmcp call src/openukpublicdata_mcp/server.py lookup_postcode postcode='SW1A 1AA' --json
```

## Hermes MCP config

After the server is stable, register it with Hermes using `hermes config set` rather than editing config files directly:

```bash
hermes config set mcp_servers.openukpublicdata.command "/home/stephen/projects/OpenUKPublicDataMCP/.venv/bin/python"
hermes config set mcp_servers.openukpublicdata.args '["-m", "openukpublicdata_mcp.server"]'
hermes config set mcp_servers.openukpublicdata.timeout 120
hermes config set mcp_servers.openukpublicdata.connect_timeout 60
```

Restart Hermes after changing MCP config.

## Web explorer

```bash
./scripts/run-web.sh
# http://127.0.0.1:8765
```

See `web/README.md` for dev mode (Vite + API).

## Research

See `research/LINKS.md` and `research/github-projects/` for the first competitor/source notes.
