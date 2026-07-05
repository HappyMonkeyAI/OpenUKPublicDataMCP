"""GOV.UK Search API adapter."""

from __future__ import annotations

from typing import Any

from openukpublicdata_mcp.http import get_json

SEARCH_URL = "https://www.gov.uk/api/search.json"


async def search(query: str, limit: int) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = await get_json(SEARCH_URL, params={"q": query, "count": limit})
    results = []
    for item in payload.get("results", [])[:limit]:
        results.append(
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "description": item.get("description"),
                "public_timestamp": item.get("public_timestamp"),
                "content_store_document_type": item.get("content_store_document_type"),
                "organisations": item.get("organisations"),
            }
        )
    data = {"query": query, "total": payload.get("total"), "results": results}
    return data, {"total": payload.get("total")}