# UK public data source priority catalogue

Curated from GOV.UK API catalogue (`co-cddo/api-catalogue`), live smoke tests (2026-07-05), and `research/LINKS.md`. Use this to decide **v1 no-key** vs **optional-key** vs **backlog**.

## Tier A — Implemented (no key)

| Source | API base | MCP tools | Notes |
|--------|----------|-----------|-------|
| GOV.UK Search | `www.gov.uk/api/search.json` | `search_govuk` | Official releases, guidance |
| data.gov.uk CKAN | `data.gov.uk/api/action` | `search_public_datasets` | Dataset discovery |
| postcodes.io | `api.postcodes.io` | `lookup_postcode` | Community; ONSPD-derived |
| GOV.UK bank holidays | `www.gov.uk/bank-holidays.json` | `get_bank_holidays` | Calendar JSON |
| Carbon Intensity | `api.carbonintensity.org.uk` | `get_carbon_intensity` | GB grid signal |
| EA flood monitoring | `environment.data.gov.uk/flood-monitoring` | `list_flood_warnings`, `search_flood_areas` | England |
| ONS Beta API | `api.beta.ons.gov.uk/v1` | `search_ons_datasets`, `get_ons_dataset`, `get_ons_latest_version`, `get_ons_observations`, `get_cpih_inflation_headline` | Search, metadata, observations |
| planning.data.gov.uk | `www.planning.data.gov.uk` | `search_planning_applications` | England planning entities |
| data.police.uk | `data.police.uk/api` | `police_street_crime_near` | Street crime near lat/lng |
| UK Parliament Members API | `members-api.parliament.uk` | `search_mp_by_postcode`, `search_constituencies` | MP + constituency drill-down |

## Tier B — Optional key (registry + partial tools)

| Source | Env | MCP status |
|--------|-----|------------|
| Companies House | `COMPANIES_HOUSE_API_KEY` | `companies_house_company_profile` (auth_required without key) |
| Ordnance Survey Places | `OS_PLACES_API_KEY` | `os_places_find_place` |
| TfL Unified | `TFL_APP_ID`, `TFL_APP_KEY` | `tfl_line_status` |
| Met Office Weather DataHub | `MET_OFFICE_DATAHUB_API_KEY` | `met_office_site_forecast` (Global Spot; register at datahub.metoffice.gov.uk) |

## Tier C — High value backlog (no-key or key TBC)

| Source | Why | Blocker |
|--------|-----|---------|
| Parliament Hansard / bills | Debates, legislation | TheyWorkForYou API key or heavier Parliament APIs |
| Legislation.gov.uk | Primary legislation | SPARQL/XML; heavier adapter |
| NHS ODS / NHSBSA | Health orgs, prescribing | Sector-specific |
| Defra UK-AIR SOS | Air quality measurements | OGC SOS; thin JSON adapter backlog |
| Land Registry Price Paid | Property | Bulk/open data mix |
| Open Banking (read-only public) | N/A | Not government |

## Tier D — Deprioritise for agent MCP

- Full mirror of ~244 catalogue APIs — use discovery tools instead.
- Scraping-only sites without stable JSON APIs.
- Duplicate hobby MCPs without maintenance (label in `research/github-projects/`).

## Selection rules (product)

1. **Agent question frequency** — economy, place, energy, floods, companies, weather, democracy.
2. **No-key or easy key** — prefer Tier A for default Hermes profile.
3. **Citation** — official + licence in envelope (ADR 0001).
4. **Payload size** — steer via `cap_envelope` / proxy `token_budget` (DynamicMCPProxy S-12).

## Maintenance

Re-run catalogue mine periodically:

```bash
curl -sSL https://raw.githubusercontent.com/co-cddo/api-catalogue/main/data/catalogue.csv \
  | rg -i 'ons|environment|companies|transport|open data'
```

Update this file when adding tools; link ADRs in `docs/adr/`.

See also: `research/notes/2026-07-05-uk-enrichment-met-office-parliament.md`.