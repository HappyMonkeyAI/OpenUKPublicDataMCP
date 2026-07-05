# Codex lane — task-006 ONS observations

Repo: /home/stephen/projects/OpenUKPublicDataMCP
Read AGENTS.md and CONTEXT.md first. Claim task-006 via scripts if still pending.

## Already done (do NOT redo)
- search_ons_datasets, get_ons_dataset in adapters/ons.py
- Flood adapters, Companies House optional-key stub
- 17 pytest tests passing

## Your scope ONLY
Implement ONS Beta API **latest edition/version resolution** and **observations** fetch.

### API (no key)
- GET https://api.beta.ons.gov.uk/v1/datasets/{id}
- GET https://api.beta.ons.gov.uk/v1/datasets/{id}/editions
- GET https://api.beta.ons.gov.uk/v1/datasets/{id}/editions/{edition}/versions
- GET .../versions/{version}/observations?time=*&geography=... (start with minimal params; document in docstring)

### Deliverables
1. Extend `src/openukpublicdata_mcp/adapters/ons.py`:
   - `resolve_latest_version(dataset_id) -> tuple[data, upstream]`
   - `get_observations(dataset_id, edition=None, version=None, limit=20) -> tuple[data, upstream]` (auto-resolve latest when edition/version omitted)
2. MCP tools in `server.py`: `get_ons_latest_version`, `get_ons_observations` (use envelope + cap_envelope)
3. `tests/test_server.py` respx mocks for edition/version/observations chain
4. Update `planning.py` standard/deep steps to include `get_ons_observations` where appropriate
5. Update `docs/tests/live-smoke-commands.md` with two example fastmcp calls
6. Do NOT edit `providers/os_places.py`, `providers/tfl.py` (agy lane)

### Verification (required before finish)
```bash
cd /home/stephen/projects/OpenUKPublicDataMCP && . .venv/bin/activate && pytest -q && python -m compileall -q src tests
```

### Git
Commit with message: `feat(ons): latest version and observations tools (task-006)`

Return: list of files changed, pytest output, tool names added.