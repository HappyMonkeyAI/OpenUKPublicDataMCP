# UK Public Data — Q2 2026 Executive Snapshot (Test Brief)

**Prepared:** 5 July 2026  
**Method:** OpenUKPublicDataMCP smoke test + official source verification (GOV.UK, ONS, data.gov.uk, Carbon Intensity API)  
**Scope note:** As of this date, many “Q2 2026” headline statistics are not yet published as full-quarter releases. This brief uses the latest official figures available for April–June 2026 and Q1 2026 where Q2 aggregates are pending.

---

## Headline

The UK entered the second quarter of 2026 with **modest growth momentum from Q1**, **inflation stable at 2.8%**, a **mixed labour market** (more jobs, higher unemployment), **consumer activity rebounding in May**, **house prices still rising**, and **electricity carbon intensity averaging ~116 gCO₂/kWh** over the quarter—while the live grid reading on test day was **62 gCO₂/kWh (low)**.

---

## 1. Economy

| Indicator | Latest official signal | Period |
|-----------|------------------------|--------|
| Real GDP growth | **+0.6%** (quarter-on-quarter) | Q1 2026 |
| Nominal GDP | **+1.6%** QoQ; **+4.6%** YoY | Q1 2026 |
| Monthly GDP | April 2026 release is latest monthly slice | April 2026 |

**Read:** Q2 began from a stronger Q1 base; a complete Q2 GDP picture was not yet available at time of writing.

**Sources:** ONS — [GDP first quarterly estimate, UK: January to March 2026](https://www.ons.gov.uk/economy/grossdomesticproductgdp/bulletins/gdpfirstquarterlyestimateuk/januarytomarch2026); [GDP monthly estimate, UK: April 2026](https://www.ons.gov.uk/economy/grossdomesticproductgdp/bulletins/gdpmonthlyestimateuk/april2026).

---

## 2. Inflation

- **CPI:** **2.8%** in the 12 months to **May 2026** (unchanged from April).
- **Implication:** Inflation was not accelerating through the first two months of Q2 but remained above the Bank of England **2%** target.

**Source:** ONS — [Consumer price inflation, UK: May 2026](https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/consumerpriceinflation/may2026).

---

## 3. Labour market

| Measure | Figure | Period |
|---------|--------|--------|
| Workforce jobs | **36.8m** (+256k / +0.7% vs Dec 2025) | March 2026 |
| Unemployment (16+) | **5.0%** (+0.5 pp vs prior year) | Jan–Mar 2026 |

**Read:** Job stock expanded, but unemployment was elevated—consistent with a labour market that is expanding in headcount while slack persists.

**Sources:** ONS — [Labour market overview, UK: June 2026](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/uklabourmarket/june2026); [Labour market overview, UK: May 2026](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/uklabourmarket/may2026).

---

## 4. Consumers & high street

- **Retail sales volumes:** **+1.2%** in May 2026, after **−1.0%** in April (volume measure).
- **Retail footfall (real-time indicators):** District/local centres and town/city centres both **+9%** vs April 2026.

**Read:** May looked like a rebound month for spending and footfall, not a straight-line slowdown.

**Sources:** ONS — [Retail sales, Great Britain: May 2026](https://www.ons.gov.uk/businessindustryandservice/retailindustry/bulletins/retailsales/may2026); [Economic activity and social change, UK: real-time indicators, 18 June 2026](https://www.ons.gov.uk/economy/economicoutputandproductivity/output/bulletins/economicactivityandsocialchangeintheukrealtimeindicators/18june2026).

---

## 5. Housing

- **UK HPI (April 2026):** Average prices **+0.7%** month-on-month; **+3.8%** year-on-year.
- **England average price:** **£291,000** (+3.9% / +£10,000 YoY).

**Source:** GOV.UK / ONS — [UK House Price Index: April 2026](https://www.gov.uk/government/statistics/uk-house-price-index-for-april-2026); [Private rent and house prices, UK: June 2026](https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/privaterentandhousepricesuk/june2026).

---

## 6. Energy & carbon

**Live MCP test (`get_carbon_intensity`):**

| Field | Value |
|-------|-------|
| Period | 2026-07-05 14:00–14:30 UTC |
| Actual intensity | **62 gCO₂/kWh** |
| Index | **low** |

**Q2 2026 aggregate (Carbon Intensity API, half-hourly series):**

| Statistic | Value |
|-----------|-------|
| Window | 2026-04-01 → 2026-06-30 |
| Observations | 4,368 |
| Mean actual intensity | **116.2 gCO₂/kWh** |
| Min / max | 20 / 256 |

**Read:** Same-day grid was unusually clean vs the quarter average—useful reminder to cite both spot and period aggregates.

**Source:** National Grid ESO — [Carbon Intensity API](https://api.carbonintensity.org.uk/) via OpenUKPublicDataMCP.

---

## 7. Public dataset discovery (MCP)

`search_public_datasets` for *“UK economy quarterly 2026”* returned **343** catalogue hits. Example high-signal dataset surfaced in testing:

- **FCA whistleblowing quarterly data 2026 Q1** — 355 reports, 906 allegations (Jan–Mar 2026); licence: Open Government Licence.

**Source:** data.gov.uk CKAN API via OpenUKPublicDataMCP.

---

## 8. ONS dataset discovery (MCP — post task-003)

`search_ons_datasets` for *“consumer price inflation”* surfaces official dataset IDs (e.g. **cpih01**). `get_ons_dataset` returns **release_frequency**, **last_updated**, and **links** to editions/versions for agent-driven time-series pulls (observations tool planned next).

**Example workflow:**

```bash
fastmcp call src/openukpublicdata_mcp/server.py:mcp search_ons_datasets query='GDP' limit=5 --json
fastmcp call src/openukpublicdata_mcp/server.py:mcp get_ons_dataset dataset_id='cpih01' --json
```

**Source:** ONS Beta API via OpenUKPublicDataMCP.

---

## MCP test verdict

| Check | Result |
|-------|--------|
| `search_govuk` | OK — surfaced ONS/GOV.UK releases |
| `search_public_datasets` | OK — dataset discovery at scale |
| `get_carbon_intensity` | OK — live envelope with source metadata |
| `search_ons_datasets` / `get_ons_dataset` | OK — official dataset IDs + metadata (reduces search-only macro gap) |
| Quarterly macro synthesis | **Improved** — use ONS tools for dataset IDs; **observations** endpoint still backlog |

**Recommended build priority:** `get_ons_observations` (or latest edition/version helper) so CPI/GDP series land in one tool call.

---

## Citations & licence

Official statistics: **Office for National Statistics** and **GOV.UK** (Open Government Licence where stated). Carbon intensity: **National Grid ESO**. Community geodata: **postcodes.io** (see upstream licence). This document is a **test artefact** for OpenUKPublicDataMCP validation, not an official statistical publication.