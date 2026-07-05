"""data.police.uk street-level crime (open, no key)."""

from __future__ import annotations

from typing import Any

from openukpublicdata_mcp.http import get_json

BASE = "https://data.police.uk/api"


async def street_crime_near(
    latitude: float,
    longitude: float,
    *,
    date: str | None = None,
    limit: int = 20,
) -> tuple[dict[str, Any], dict[str, Any]]:
    params: dict[str, Any] = {}
    if date:
        params["date"] = date
    payload = await get_json(
        f"{BASE}/crimes-street/all-crime",
        params={"lat": latitude, "lng": longitude, **params},
    )
    crimes = []
    if isinstance(payload, list):
        for item in payload[:limit]:
            crimes.append(
                {
                    "category": item.get("category"),
                    "month": item.get("month"),
                    "location": item.get("location"),
                    "outcome_status": item.get("outcome_status"),
                }
            )
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "date_filter": date,
        "count": len(crimes),
        "crimes": crimes,
    }
    return data, {"raw_count": len(payload) if isinstance(payload, list) else 0}