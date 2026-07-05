"""Planning Data platform (planning.data.gov.uk) adapters."""

from __future__ import annotations

from typing import Any

from openukpublicdata_mcp.http import get_json

ENTITY_URL = "https://www.planning.data.gov.uk/entity.json"


async def search_applications(
    *,
    dataset: str = "planning-application",
    reference: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    params: dict[str, Any] = {
        "dataset": dataset,
        "limit": limit,
        "offset": offset,
    }
    if reference:
        params["reference"] = reference.strip()
    payload = await get_json(ENTITY_URL, params=params)
    applications = []
    for entity in payload.get("entities", [])[:limit]:
        applications.append(
            {
                "entity": entity.get("entity"),
                "reference": entity.get("reference"),
                "description": entity.get("description"),
                "decision_date": entity.get("decision-date"),
                "entry_date": entity.get("entry-date"),
                "organisation_entity": entity.get("organisation-entity"),
                "dataset": entity.get("dataset"),
            }
        )
    data = {
        "dataset": dataset,
        "reference_filter": reference,
        "count": len(applications),
        "total_reported": payload.get("count"),
        "offset": offset,
        "applications": applications,
    }
    upstream = {"links": payload.get("links"), "count": payload.get("count")}
    return data, upstream