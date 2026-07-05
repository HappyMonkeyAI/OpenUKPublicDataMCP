"""Environment Agency flood monitoring adapters."""

from __future__ import annotations

from typing import Any

from openukpublicdata_mcp.http import get_json

FLOODS_URL = "https://environment.data.gov.uk/flood-monitoring/id/floods"
AREAS_URL = "https://environment.data.gov.uk/flood-monitoring/id/floodAreas"


async def list_warnings(limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = await get_json(FLOODS_URL, params={"_limit": limit})
    items = []
    for item in payload.get("items", [])[:limit]:
        area = item.get("floodArea") or {}
        items.append(
            {
                "id": item.get("@id"),
                "severity": item.get("severity"),
                "severity_level": item.get("severityLevel"),
                "description": item.get("description"),
                "message": item.get("message"),
                "time_raised": item.get("timeRaised"),
                "flood_area": area.get("notation") or area.get("label"),
                "county": area.get("county"),
                "river": area.get("riverOrSea"),
            }
        )
    data = {"count": len(items), "warnings": items}
    upstream = {"meta": payload.get("meta")}
    return data, upstream


async def search_areas(query: str, limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = await get_json(AREAS_URL, params={"search": query, "_limit": limit})
    areas = []
    for item in payload.get("items", [])[:limit]:
        areas.append(
            {
                "id": item.get("@id"),
                "notation": item.get("notation"),
                "label": item.get("label"),
                "county": item.get("county"),
                "river_or_sea": item.get("riverOrSea"),
                "lat": item.get("lat"),
                "long": item.get("long"),
            }
        )
    data = {"query": query, "count": len(areas), "areas": areas}
    upstream = {"meta": payload.get("meta")}
    return data, upstream