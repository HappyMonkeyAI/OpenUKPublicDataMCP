# UK Public Data — Q2 2026 Executive Snapshot (Test Brief)

**Prepared:** 5 July 2026 (refreshed 15:30 UTC)  
**Method:** OpenUKPublicDataMCP live MCP envelopes + official source verification (GOV.UK, ONS, data.gov.uk, Carbon Intensity API)  
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
| Period | 2026-07-05 14:30–15:00 UTC |
| Actual intensity | **72 gCO₂/kWh** |
| Forecast | 58 gCO₂/kWh |
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

## 8. ONS time series (MCP — task-006)

`get_ons_latest_version('cpih01')` → **version 67**, release **2026-02-18**.  
`get_ons_observations('cpih01', limit=5)` → **457** observations in series (UK aggregate **CP00**); sample index levels include **Jul-24: 132.9**, **Mar-24: 131.6**.

**Workflow:**

```bash
fastmcp call src/openukpublicdata_mcp/server.py get_ons_latest_version dataset_id=cpih01
fastmcp call src/openukpublicdata_mcp/server.py get_ons_observations dataset_id=cpih01 limit=5
```

**Source:** ONS Beta API via OpenUKPublicDataMCP — **retrieved 2026-07-05T15:29:49Z**.

---

## 9. Regional framing (`lookup_postcode`)

Postcode lookup anchors exec briefs to **official geography labels** (not regional CPI/GDP splits unless you add ONS dimension filters).

| Postcode | Region | District | Constituency |
|----------|--------|----------|--------------|
| **SW1A 1AA** | London | Westminster | Cities of London and Westminster |
| **M1 1AE** | North West | Manchester | Manchester Central |

**Tool:** `lookup_postcode` — postcodes.io — **retrieved 2026-07-05T15:29:49Z**.

---

## 10. Planning data (MCP — task-009)

`search_planning_applications` queries **planning.data.gov.uk** (`planning-application` dataset). Platform reports **100k+** applications nationally; use `reference` filter for precise lookups.

**Source:** MHCLG Planning Data API — Open Government Licence.

---

## MCP test verdict

| Check | Result |
|-------|--------|
| `search_govuk` | OK |
| `search_public_datasets` | OK |
| `get_carbon_intensity` | OK — live envelope |
| `search_ons_datasets` / `get_ons_dataset` | OK |
| `get_ons_latest_version` / `get_ons_observations` | OK — CPIH v67 + observations |
| `lookup_postcode` | OK — regional framing |
| `search_planning_applications` | OK — England planning API |
| Quarterly macro synthesis | **Good** — combine bulletin headlines (§2) with API series (§8) |

**Next build priority:** ONS % change helper; postcode→planning geography filters when API supports them.

---

## Citations & licence

Official statistics: **Office for National Statistics** and **GOV.UK** (Open Government Licence where stated). Carbon intensity: **National Grid ESO**. Community geodata: **postcodes.io** (see upstream licence). This document is a **test artefact** for OpenUKPublicDataMCP validation, not an official statistical publication.