# CONTEXT — OpenUKPublicDataMCP

## Mission

Build an agent-grade MCP gateway for high-value UK public data. The project should be more reliable and product-shaped than existing hobby aggregators: no-key-first, source-cited, tested, and deployable as stdio or HTTP.

## Stack

- Python 3.11+
- FastMCP
- httpx for upstream HTTP APIs
- pytest/respx for tests
- pyproject.toml package layout under `src/`

## Non-negotiables

1. Core tools must work without API keys.
2. Optional-key sources must be clearly labelled and must not break no-key startup.
3. Every external response returned by a tool must include source metadata.
4. Prefer official UK public-sector APIs. If using a community source, label it.
5. Stdio mode must not print banners/logs to stdout. MCP protocol owns stdout.
6. Keep tools agent-friendly. Do not mirror every upstream endpoint blindly.
7. Never commit `.env` or real API keys.

## Tool response contract

Return JSON-safe dicts with:

- `data`: normalized result
- `source`: registry metadata including URL, auth mode, official flag, licence if known
- `retrieved_at`: ISO timestamp
- `upstream`: compact raw upstream payload when useful

Errors should include source name, HTTP status when available, and safe context. Do not expose secrets.

## Source tiers

- Tier 1: official API, no key required
- Tier 2: official API, optional/free key required
- Tier 3: official downloadable dataset requiring local cache/index
- Tier 4: public/community API derived from official data
- Tier 5: scraped/fragile source — avoid in core

## Initial source registry

Core no-key:
- GOV.UK Bank Holidays
- GOV.UK Search
- data.gov.uk CKAN API
- postcodes.io
- National Grid ESO Carbon Intensity API
- Environment Agency flood monitoring
- ONS Beta API

Optional-key candidates:
- Companies House
- EPC register
- Ordnance Survey Data Hub
- TfL
- Met Office DataHub

## Workflow

- Add one source adapter at a time.
- Add tests with mocked upstream calls before broad live tests.
- For each source, update `src/openukpublicdata_mcp/sources.py`, README tools list, and research/source notes.
- Use ADRs for architectural choices that affect source registry, caching, deployment, or optional credentials.

## What not to do

- Do not claim “all UK government APIs”. Use “high-value UK public data sources”.
- Do not require signup for the base server.
- Do not hide auth requirements.
- Do not rely on scraping where an API/download exists.
- Do not let a broken optional provider fail server startup.
