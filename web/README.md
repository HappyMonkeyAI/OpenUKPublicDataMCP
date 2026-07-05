# OpenUK Public Data Explorer (web/)

React + Leaflet UI for browsing UK public data via the FastAPI bridge (`openukpublicdata_mcp.rest_api`).

## Features

- **Top search** — GOV.UK, ONS datasets, data.gov.uk catalogue, UK postcodes (with constituency resolution).
- **Topic explorer** — economy, energy, floods, place, planning, crime, catalogue.
- **Map** — UK regions/nations (click to drill); postcode search zooms to constituency context.
- **Detail panel** — live JSON envelopes from the same functions as the MCP server.

## Run (production-style)

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP
./scripts/run-web.sh
```

Open http://127.0.0.1:8765 (API serves built `web/dist`).

## Run (development)

Terminal 1:

```bash
. .venv/bin/activate
pip install -e '.[web]'
OPENUK_WEB_PORT=8765 openukpublicdata-web
```

Terminal 2:

```bash
cd web && npm run dev
```

Open http://127.0.0.1:5173 (Vite proxies `/api` to port 8765).

## Build only

```bash
cd web && npm install && npm run build
```