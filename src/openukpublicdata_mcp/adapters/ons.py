"""ONS Beta API adapters."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from openukpublicdata_mcp.http import get_json

SEARCH_URL = "https://api.beta.ons.gov.uk/v1/search"


async def search_datasets(query: str, limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = await get_json(SEARCH_URL, params={"q": query, "size": limit})
    items = payload.get("items", [])[:limit]
    datasets = []
    for item in items:
        datasets.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("description"),
                "release_date": item.get("release_date"),
                "last_updated": item.get("last_updated"),
                "url": f"https://www.ons.gov.uk/datasets/{item.get('id')}" if item.get("id") else None,
            }
        )
    data = {"query": query, "count": len(datasets), "datasets": datasets}
    upstream = {"count": payload.get("count")}
    return data, upstream


async def get_dataset(dataset_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    cleaned = dataset_id.strip()
    payload = await get_json(f"https://api.beta.ons.gov.uk/v1/datasets/{quote(cleaned)}")
    data = {
        "id": payload.get("id"),
        "title": payload.get("title"),
        "description": payload.get("description"),
        "release_frequency": payload.get("release_frequency"),
        "last_updated": payload.get("last_updated"),
        "next_release": payload.get("next_release"),
        "keywords": payload.get("keywords"),
        "contacts": payload.get("contacts"),
        "links": payload.get("links"),
    }
    upstream = {"id": payload.get("id")}
    return data, upstream