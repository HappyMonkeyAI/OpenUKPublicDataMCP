# Executive report 3 — Climate & resilience ops brief

**Audience:** Facilities, logistics, operations, local resilience planning  
**Generated:** 5 July 2026 (UTC)  
**Engine:** OpenUKPublicDataMCP (no API keys)

---

## Executive summary

**Operational** UK signals—**electricity carbon intensity now** and **flood warning state in England**—are available in a single agent session without credentials. At test time the GB grid was in a **low** carbon band (**72 gCO₂/kWh** actual vs **58** forecast for the half-hour ending 15:00Z), and the Environment Agency API returned **zero** active warnings in the polled set. Use this brief for **near-real-time ops dashboards**; pair with Met Office / EA GOV.UK pages for forecast narrative.

---

## 1. Electricity carbon intensity (Great Britain)

**Current half-hour** (from `get_carbon_intensity`):

| From (UTC) | To (UTC) | Forecast | Actual | Index |
|------------|----------|----------|--------|-------|
| 2026-07-05T14:30Z | 2026-07-05T15:00Z | 58 | **72** | **low** |

**Ops read:** Favour lower-carbon scheduling (EV charging, batch compute, flexible load) when `index` is **low** and actual intensity is below quarterly norms.

**Source:** National Grid ESO Carbon Intensity API  
**Docs:** https://carbon-intensity.github.io/api-definitions/  
**Tool:** `get_carbon_intensity`  
**Retrieved:** 2026-07-05T15:18:21Z

**Context:** Q2 2026 average intensity ~**116 gCO₂/kWh** (see `Q2-executive-report.md`) — today’s reading is **materially below** that quarterly average.

---

## 2. Flood warnings (England)

**Poll:** `list_flood_warnings(limit=10)`

| Active warnings returned | Severities in set |
|--------------------------|-------------------|
| **0** | n/a |

**Ops read:** No EA flood warnings in the top-10 poll at retrieval. Re-poll during storms; use `search_flood_areas` for area IDs by name/postcode context.

**Source:** Environment Agency — https://environment.data.gov.uk/flood-monitoring  
**Licence:** Open Government Licence v3  
**Tool:** `list_flood_warnings`  
**Retrieved:** 2026-07-05T15:18:23Z

---

## 3. GOV.UK resilience pointers

`search_govuk('flood warnings environment agency', limit=3)` surfaced:

| Title | Path |
|-------|------|
| Prepare for flooding | `/prepare-for-flooding` |
| EA news (historical flood alerts) | `/government/news/...` |

**Tool:** `search_govuk`  
**Retrieved:** 2026-07-05T15:18:23Z

Use for **human procedures**; API for **machine status**.

---

## 4. Suggested ops checklist (automated)

1. `get_carbon_intensity` — every 30 min for scheduling hints.  
2. `list_flood_warnings` — hourly during yellow/amber weather.  
3. `search_govuk` — weekly for EA/Met Office policy updates.  
4. Optional: `lookup_postcode` to anchor sites before flood area search.

---

## Reproduce

```bash
fastmcp call src/openukpublicdata_mcp/server.py get_carbon_intensity
fastmcp call src/openukpublicdata_mcp/server.py list_flood_warnings limit=10
fastmcp call src/openukpublicdata_mcp/server.py search_govuk query='prepare for flooding' limit=3
```

---

## Gaps

- No Met Office weather in v1 server (backlog — API key).  
- Flood monitoring is **England**; Scotland/Wales/Northern Ireland need other sources.  
- Carbon API is **GB electricity**, not full scope 3 / gas heating.

**Companion:** `exec-01-quarterly-uk-public-data-pulse.md`