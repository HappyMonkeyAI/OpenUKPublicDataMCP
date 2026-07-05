# ADR 0002 — Optional-key provider modules

## Status

Accepted

## Context

ADR 0001 limits the **core** server to no-key tools. High-value UK sources (Companies House, Ordnance Survey Places, TfL Unified API) require API keys or OAuth. Agents must not crash or leak when keys are absent; `list_sources` must still advertise what *could* be enabled.

## Decision

1. **Registry:** Every provider has a `Source` row with `auth: optional_key | required_key`.
2. **Environment:** Keys live only in process env (`.env` locally, never committed). Document names in `.env.example`.
3. **Tool behaviour when key missing:**
   - Return HTTP 200-style **envelope** with `data.status = "auth_required"`, `data.message`, and `source` metadata — do not raise to the MCP client.
4. **Tool behaviour when key present:** Normal upstream call + cited envelope.
5. **Implementation layout:** `src/openukpublicdata_mcp/providers/<name>.py` — thin wrappers; `server.py` only registers tools that import providers.
6. **No-key default:** `list_sources(auth="none")` excludes optional-key sources unless `auth="all"`.

## Initial optional providers (stubs → full adapters)

| Provider | Env var | Status |
|----------|---------|--------|
| Companies House | `COMPANIES_HOUSE_API_KEY` | stub tool `companies_house_company_profile` |
| Ordnance Survey Places | `OS_PLACES_API_KEY` | registry only (task backlog) |
| TfL Unified API | `TFL_APP_ID`, `TFL_APP_KEY` | registry only (task backlog) |

## Consequences

- Agents see honest `auth_required` instead of opaque 401 stack traces.
- Optional modules can ship incrementally without breaking no-key-first positioning.
- Operators must load `.env` in MCP client config (`env` block in catalogue / Hermes `mcp_servers`).

## References

- `research/LINKS.md`
- GOV.UK API catalogue (`co-cddo/api-catalogue`)
- DynamicMCPProxy `env_vars` on catalogue entries