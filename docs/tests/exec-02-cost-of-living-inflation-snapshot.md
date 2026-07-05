# Executive report 2 — Cost of living / inflation snapshot

**Audience:** SMEs, retail, hospitality, finance leads  
**Generated:** 5 July 2026 (UTC)  
**Engine:** OpenUKPublicDataMCP (no API keys)

---

## Executive summary

Official **inflation intelligence** can be assembled in one pass: discover ONS datasets, pull **CPIH** metadata and **latest published version**, and sample **index observations** from the ONS Beta API, while cross-linking **data.gov.uk** packages and **GOV.UK** guidance. Latest CPIH API version **67** was published **18 February 2026**. For **policy-facing % change headlines**, cite ONS statistical bulletins; this report emphasises **machine-readable** CPIH index levels and catalogue paths agents can automate.

---

## CPIH at a glance (ONS API)

| Item | Detail |
|------|--------|
| Dataset ID | `cpih01` |
| Title | Consumer Prices Index including owner occupiers' housing costs (CPIH) |
| Frequency | Monthly |
| Latest version | **67** |
| Release date (version) | **2026-02-18** |
| Contact | cpi@ons.gov.uk — Consumer Price Inflation team |

**Description (abridged):** CPIH extends CPI with owner occupiers' housing costs and council tax; monthly series from 2005.

**Downloads (version 67):**

- CSV: https://download.ons.gov.uk/downloads/datasets/cpih01/editions/time-series/versions/67.csv  
- XLS: https://download.ons.gov.uk/downloads/datasets/cpih01/editions/time-series/versions/67.xlsx  

**Tools:** `get_ons_dataset`, `get_ons_latest_version`  
**Source:** ONS Beta API — Open Government Licence  
**Retrieved:** 2026-07-05T15:18:24Z

---

## Observations sample (UK, all-items aggregate CP00)

MCP call: `get_ons_observations(dataset_id='cpih01', limit=5)`  
Resolved query: `time=*`, geography `K02000001`, aggregate `CP00`  
Upstream reports **457** observations in full series; envelope returns first **5** per limit.

| Time | CPIH index |
|------|------------|
| Jul-24 | 132.9 |
| Mar-24 | 131.6 |
| May-23 | 129.1 |
| Jul-23 | 129.0 |
| Oct-22 | 124.3 |

**Interpretation:** Values are **index levels** (2015=100 style ONS indexing), not month-on-month % rates. For exec slides on “inflation rate”, use ONS bulletin tables or derive % from consecutive months in the full CSV.

**Tool:** `get_ons_observations`  
**Retrieved:** 2026-07-05T15:18:25Z

---

## Discovery layer

| Channel | Result |
|---------|--------|
| `search_ons_datasets('consumer price inflation')` | Multiple *Consumer price inflation, UK* releases listed (ONS search index) |
| `search_public_datasets('consumer price inflation UK')` | **35** datasets; includes ONS *Consumer Price Inflation* package |
| `search_govuk('inflation statistics ONS')` | Broad GOV.UK index — refine query to `site:ons.gov.uk CPI` for releases |

---

## Suggested one-liner for leadership

> “We can monitor **CPIH** programmatically on **`cpih01`** (version **67**, Feb 2026), with **457** monthly observations available via API, alongside **35** related open datasets on data.gov.uk — no API key required for the core chain.”

---

## Reproduce

```bash
fastmcp call src/openukpublicdata_mcp/server.py search_ons_datasets query='consumer price inflation' limit=5
fastmcp call src/openukpublicdata_mcp/server.py get_ons_observations dataset_id=cpih01 limit=5
```

---

## Caveats

- Dimension filters matter; wrong aggregate/geography changes the series.
- GOV.UK search ranking may not surface the latest ONS bulletin first — prefer direct ONS URLs for external comms.
- Optional enrichments (`companies_house_company_profile`, etc.) do not affect inflation series.

**Companion:** `exec-01-quarterly-uk-public-data-pulse.md`, `Q2-executive-report.md` (CPI **2.8%** narrative).