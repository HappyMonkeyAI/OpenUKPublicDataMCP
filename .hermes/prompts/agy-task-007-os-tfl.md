# Agy lane — task-007 OS Places + TfL optional-key

Repo: /home/stephen/projects/OpenUKPublicDataMCP
Read AGENTS.md, docs/adr/0002-optional-key-providers.md. Claim task-007 if pending.

## Already done (do NOT redo)
- adapters/ons.py, adapters/ea_flood.py — **do not modify ons.py** (codex owns ONS observations)
- companies_house optional-key pattern in providers/companies_house.py

## Your scope ONLY
Add **Ordnance Survey Places** and **TfL Unified API** optional-key providers per ADR 0002.

### OS Places
- Env: `OS_PLACES_API_KEY`
- Provider: `src/openukpublicdata_mcp/providers/os_places.py`
- Tool: `os_places_find_place(query: str, limit: int = 5)` — auth_required without key; with key call OS Data Hub Places API (document endpoint in code comments; use httpx via get_json with header `key` or OS docs)
- Registry already has `os_places` in sources.py — wire metadata

### TfL
- Env: `TFL_APP_ID`, `TFL_APP_KEY` (query params on requests per TfL docs)
- Provider: `src/openukpublicdata_mcp/providers/tfl.py`
- Tool: `tfl_line_status(line_ids: str | None = None)` — default all lines summary; auth_required if keys missing
- Registry `tfl_unified` exists

### Tests
- `tests/test_providers.py`: auth_required cases for both tools (monkeypatch env)
- Optional respx test with fake key if easy

### Docs
- Update `.env.example` if new vars missing
- Brief bullets in README current tools

### Do NOT touch
- `adapters/ons.py`, `server.py` ONS observation tools (codex)

You MAY add new tools to server.py for os/tfl only.

### Verification
```bash
cd /home/stephen/projects/OpenUKPublicDataMCP && . .venv/bin/activate && pytest -q && python -m compileall -q src tests
```

### Git
Commit: `feat(optional-key): OS Places and TfL tools (task-007)`

Return: files changed, pytest summary.