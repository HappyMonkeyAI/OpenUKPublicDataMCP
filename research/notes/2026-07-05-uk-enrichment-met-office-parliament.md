# UK public data enrichment — Met Office, Parliament, related sources

**Date:** 2026-07-05  
**Scope:** Extend OpenUKPublicDataMCP beyond v1 core with official-adjacent UK suppliers.

## Executive summary

- **UK Parliament Members API** — **no key**, stable JSON; **implement now** (`search_mp_by_postcode`, `search_constituencies`).
- **Met Office** — **DataPoint retired**; **Weather DataHub** site-specific GeoJSON requires **`apikey` header** and free registration (Global Spot ~360 calls/day on free plan per DataHub pricing pages). **Implement as optional-key** (`met_office_site_forecast`).
- **Defra UK-AIR** — official SOS/REST exists but **no simple no-key JSON** for national station snapshots in smoke tests; **defer** thin adapter until REST path is pinned (OGC SOS is heavy for agents).
- **Police.uk** — already shipped in v1.

## Product lenses (condensed deep research)

| Lens | Finding |
|------|---------|
| Technical | Parliament `members-api.parliament.uk` returns MP by postcode; Met Office uses `data.hub.api.metoffice.gov.uk` + `apikey`. |
| Economic | Met Office free tier caps calls; optional-key fits ADR 0002. Parliament is public-task data at no marginal cost. |
| Strategic | Weather + democracy data pair with floods/carbon for “resilience briefs” (exec reports). |
| Contrarian | Open-Meteo air quality is easier but **not UK official** — avoid as default; cite if ever added. |
| First principles | Agent MCP needs **cited envelopes**, not raw portal HTML (Defra Data Services SPA). |

## Implementation plan (this session)

1. `adapters/parliament.py` + MCP tools + tests (respx).
2. `providers/met_office.py` + MCP tool + `auth_required` test.
3. Update `source-priority-catalogue.md`, `.env.example`, `rest_api.py`, `geography` topics, web search.
4. Tasks **task-014** (parliament), **task-015** (met office), **task-016** (research doc).

## Open questions

- Met Office **exact** free-tier daily cap vs marketing “360/day” — confirm in operator subscription UI.
- UK-AIR **REST** JSON examples for latest hourly PM2.5 at station — need PDF/api-doc harvest.
- **TheyWorkForYou** API key for Hansard — optional paid tier; Parliament API sufficient for MP/constituency drill-down.

## References

- https://datahub.metoffice.gov.uk/docs/getting-started  
- https://datahub.metoffice.gov.uk/support/faqs (apikey header)  
- https://members-api.parliament.uk/  
- https://www.api.gov.uk/defra/uk-air-sensor-observation-service/  
- CCC 2025 adaptation report (Met Office Local Authority Climate Service mention)