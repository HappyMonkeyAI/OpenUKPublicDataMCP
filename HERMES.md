# HERMES — Agent Guide

## Before work

1. Read `CONTEXT.md`.
2. Check `docs/adr/` for relevant decisions.
3. If comparing sources or competitors, add notes under `research/`.

## Build rules

- Use FastMCP tools with explicit typed parameters and user-facing docstrings.
- Keep adapters thin and source-cited.
- Preserve stdio discipline: no stdout logging in server runtime.
- Prefer `mcp.run(show_banner=False, log_level="WARNING")`.
- Add tests for new adapters.

## Verification

Minimum before handoff:

```bash
pytest
python -m compileall src tests
fastmcp inspect src/openukpublicdata_mcp/server.py:mcp
fastmcp list src/openukpublicdata_mcp/server.py --json
```

For each new tool, run at least one `fastmcp call` or a focused pytest covering the tool behavior.

## Secrets

- `.env` is local only and gitignored.
- Optional API keys belong in environment variables.
- Never log credentials or put them in fixtures.
