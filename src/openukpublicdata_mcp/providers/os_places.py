"""Ordnance Survey Places API (optional key)."""

from __future__ import annotations

import os
from typing import Any

from openukpublicdata_mcp.http import get_json

# OS Data Hub Places API — see https://osdatahub.os.uk/docs/places/overview
PLACES_URL = "https://api.os.uk/search/places/v1/postcode"


def os_places_api_key() -> str | None:
    return os.environ.get("OS_PLACES_API_KEY") or None


async def find_places(query: str, *, limit: int = 5) -> tuple[dict[str, Any], dict[str, Any]]:
    key = os_places_api_key()
    if not key:
        return (
            {
                "status": "auth_required",
                "message": "Set OS_PLACES_API_KEY to use Ordnance Survey Places.",
                "query": query,
            },
            {"auth": "missing"},
        )
    limit = max(1, min(limit, 20))
    # Postcode search when query looks like a postcode; otherwise use find endpoint pattern
    q = query.strip()
    if " " in q or len(q) <= 8:
        url = PLACES_URL
        params: dict[str, Any] = {"postcode": q.replace(" ", ""), "maxresults": limit}
    else:
        url = "https://api.os.uk/search/places/v1/find"
        params = {"query": q, "maxresults": limit}
    payload = await get_json(url, params=params, headers={"key": key})
    results = payload.get("results") or []
    return (
        {"query": q, "count": len(results), "results": results[:limit]},
        {"endpoint": url},
    )