"""HTTP API for the web explorer (wraps MCP tool functions)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from openukpublicdata_mcp import geography
from openukpublicdata_mcp.server import (
    get_carbon_intensity,
    get_cpih_inflation_headline,
    get_ons_observations,
    health_check,
    list_flood_warnings,
    lookup_postcode,
    police_street_crime_near,
    search_govuk,
    search_ons_datasets,
    search_planning_applications,
    search_public_datasets,
)

POSTCODE_RE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$", re.IGNORECASE)

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_DIST = REPO_ROOT / "web" / "dist"
GEO_DIR = REPO_ROOT / "web" / "public" / "geo"

app = FastAPI(title="OpenUK Public Data Explorer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def api_health() -> dict[str, Any]:
    return health_check()


@app.get("/api/explorer/topics")
async def api_explorer_topics() -> dict[str, Any]:
    return geography.explorer_topics()


@app.get("/api/geo/regions")
async def api_geo_regions() -> dict[str, Any]:
    return geography.list_regions()


@app.get("/api/geo/region/{region_id}")
async def api_geo_region(region_id: str) -> dict[str, Any]:
    region = geography.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="region_not_found")
    return region


@app.get("/api/geo/boundaries/{name}")
async def api_geo_boundaries(name: str) -> FileResponse:
    allowed = {"uk-regions": "uk-regions.geojson"}
    if name not in allowed:
        raise HTTPException(status_code=404, detail="boundary_not_found")
    path = GEO_DIR / allowed[name]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="boundary_file_missing")
    return FileResponse(path, media_type="application/geo+json")


@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(12, ge=1, le=24),
) -> dict[str, Any]:
    cleaned = q.strip()
    results: list[dict[str, Any]] = []

    normalised_pc = cleaned.upper().replace("  ", " ")
    if POSTCODE_RE.match(normalised_pc):
        try:
            pc = await lookup_postcode(normalised_pc)
            results.append({"kind": "postcode", "title": normalised_pc, "payload": pc})
        except Exception as exc:  # noqa: BLE001
            results.append({"kind": "error", "title": "postcode", "detail": str(exc)})

    gov = await search_govuk(cleaned, limit=5)
    for row in gov["data"].get("results", [])[:5]:
        results.append(
            {
                "kind": "govuk",
                "title": row.get("title"),
                "link": row.get("link"),
                "description": row.get("description"),
            }
        )

    ons = await search_ons_datasets(cleaned, limit=5)
    for row in ons["data"].get("datasets", [])[:5]:
        results.append(
            {
                "kind": "ons_dataset",
                "title": row.get("title"),
                "id": row.get("id"),
                "url": row.get("url"),
            }
        )

    dgu = await search_public_datasets(cleaned, limit=5)
    for row in dgu["data"].get("results", [])[:5]:
        results.append(
            {
                "kind": "dataset",
                "title": row.get("title"),
                "url": row.get("url"),
                "organisation": row.get("organisation"),
            }
        )

    return {"query": cleaned, "count": len(results), "results": results[:limit]}


@app.get("/api/postcode/{postcode}")
async def api_postcode(postcode: str) -> dict[str, Any]:
    return await lookup_postcode(postcode)


@app.get("/api/carbon")
async def api_carbon() -> dict[str, Any]:
    return await get_carbon_intensity()


@app.get("/api/floods")
async def api_floods(limit: int = Query(10, ge=1, le=30)) -> dict[str, Any]:
    return await list_flood_warnings(limit=limit)


@app.get("/api/inflation/cpih")
async def api_cpih() -> dict[str, Any]:
    return await get_cpih_inflation_headline()


@app.get("/api/ons/observations")
async def api_ons_observations(
    dataset_id: str = "cpih01",
    limit: int = Query(12, ge=1, le=50),
) -> dict[str, Any]:
    return await get_ons_observations(dataset_id, limit=limit)


@app.get("/api/planning")
async def api_planning(limit: int = Query(5, ge=1, le=20)) -> dict[str, Any]:
    return await search_planning_applications(limit=limit)


@app.get("/api/crime/near")
async def api_crime_near(
    lat: float,
    lng: float,
    date: str | None = None,
    limit: int = Query(10, ge=1, le=30),
) -> dict[str, Any]:
    return await police_street_crime_near(lat, lng, date=date, limit=limit)


@app.get("/api/crime/by-postcode/{postcode}")
async def api_crime_by_postcode(
    postcode: str,
    date: str | None = None,
    limit: int = Query(10, ge=1, le=30),
) -> dict[str, Any]:
    place = await lookup_postcode(postcode)
    lat = place["data"].get("latitude")
    lng = place["data"].get("longitude")
    if lat is None or lng is None:
        raise HTTPException(status_code=422, detail="postcode_missing_coordinates")
    crime = await police_street_crime_near(lat, lng, date=date, limit=limit)
    return {"place": place, "crime": crime}


if WEB_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        index = WEB_DIST / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="web_build_missing")


def main() -> None:
    import os

    import uvicorn

    uvicorn.run(
        "openukpublicdata_mcp.rest_api:app",
        host="0.0.0.0",
        port=int(os.environ.get("OPENUK_WEB_PORT", "8765")),
        reload=False,
    )


if __name__ == "__main__":
    main()