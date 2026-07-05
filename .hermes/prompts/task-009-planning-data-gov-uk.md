# Task 009 — planning.data.gov.uk adapter

**Status:** Implemented by hermes-lane (2026-07-05).

## Delivered

- `src/openukpublicdata_mcp/adapters/planning_data.py`
- `search_planning_applications` MCP tool
- Source `planning_data_gov_uk` in registry
- Tests in `tests/test_server.py`
- Smoke commands in `docs/tests/live-smoke-commands.md`

## Follow-ups (future tasks)

- Filter by LPA / geography / date (`start_date_*` API params)
- Link with `lookup_postcode` for area briefs
- Rate-limit handling and pagination helpers