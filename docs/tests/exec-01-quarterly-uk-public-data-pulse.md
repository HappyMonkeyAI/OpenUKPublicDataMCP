# Executive report 1 — Quarterly UK public-data pulse

**Template:** Quarterly macro + official-data signals  
**Period focus:** Q2 2026 (with Q1 carry-over where Q2 aggregates pending)  
**Generated:** 5 July 2026 (UTC)  
**Engine:** OpenUKPublicDataMCP — live tool envelopes cited below

---

## Executive summary

UK public-data feeds available **without API keys** now support a **repeatable quarterly pulse**: ONS time-series (CPIH index via `get_ons_observations`), GOV.UK and data.gov.uk discovery, **live GB electricity carbon intensity**, and **England flood warning status**. At retrieval, **no active flood warnings** were returned; the grid was **low carbon intensity** (actual **72 gCO₂/kWh** for the current half-hour). ONS **CPIH** dataset **`cpih01`** is on **version 67** (published **18 Feb 2026**). Pair this automated slice with the narrative Q2 brief in `Q2-executive-report.md` for GDP/CPI headline rates from GOV.UK releases.

---

## 1. Prices — ONS CPIH (API)

| Field | Value |
|-------|--------|
| Dataset | `cpih01` — Consumer Prices Index including owner occupiers' housing costs (CPIH) |
| Latest version | **67** (`time-series` edition) |
| Version released | **2026-02-18** |
| Query used | UK geography `K02000001`, aggregate `CP00`, all times (sample `limit=5`) |

**Sample index levels returned by MCP** (CPIH index, not % change):

| Period | Index |
|--------|-------|
| Jul-24 | 132.9 |
| Mar-24 | 131.6 |
| May-23 | 129.1 |

**Read:** Use downloads on version 67 for full monthly series and official % changes; MCP proves the **observations chain** end-to-end.

**Tools:** `search_ons_datasets` → `get_ons_dataset` → `get_ons_latest_version` → `get_ons_observations`  
**Source:** ONS Beta API — https://api.beta.ons.gov.uk/v1 — Open Government Licence  
**Retrieved:** 2026-07-05T15:18:25Z (envelope `retrieved_at`)

---

## 2. Energy — GB grid (live)

| Window | Forecast | Actual | Index |
|--------|----------|--------|-------|
| 2026-07-05 14:30–15:00Z | 58 gCO₂/kWh | **72 gCO₂/kWh** | **low** |

**Tool:** `get_carbon_intensity`  
**Source:** National Grid ESO Carbon Intensity API — https://api.carbonintensity.org.uk  
**Retrieved:** 2026-07-05T15:18:21Z

*(Q2 average ~116 gCO₂/kWh from prior verified quarter analysis — see `Q2-executive-report.md`.)*

---

## 3. Resilience — England floods (live)

| Metric | Value |
|--------|-------|
| Active warnings (limit 10) | **0** |

**Tool:** `list_flood_warnings`  
**Source:** Environment Agency flood monitoring — https://environment.data.gov.uk/flood-monitoring  
**Retrieved:** 2026-07-05T15:18:23Z

---

## 4. Official narrative & catalogue

- **GOV.UK search** (`inflation statistics ONS`): large index (70k+ hits); use targeted release URLs for exec headlines.
- **data.gov.uk** (`consumer price inflation UK`): **35** packages; top hit *Consumer Price Inflation* (ONS).
- **Bank holidays** (`england-and-wales`): available via `get_bank_holidays` (payload truncated in envelope steering).

**Tools:** `search_govuk`, `search_public_datasets`, `get_bank_holidays`

---

## 5. How to reproduce

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP && . .venv/bin/activate
fastmcp call src/openukpublicdata_mcp/server.py plan_uk_public_data_research \
  topic='UK executive quarterly brief' depth=standard period='Q2 2026'
```

See `live-smoke-commands.md` for full command list.

---

## Limitations

- Q2 **headline** CPI % and GDP QoQ still best taken from **ONS bulletins** (human-facing), not raw observation samples alone.
- ONS search results may return `id: null` for some hits — prefer known dataset IDs (e.g. `cpih01`).
- Flood API covers **England**; carbon covers **Great Britain** electricity.

**Related:** `Q2-executive-report.md` (narrative Q2 test brief).