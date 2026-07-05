from __future__ import annotations

from typing import Any, Literal
from urllib.parse import quote

from fastmcp import FastMCP

from .http import get_json, utc_now_iso
from .sources import SOURCES, source_metadata

mcp = FastMCP(
    "OpenUKPublicDataMCP",
    instructions=(
        "Use this server for high-value UK public data. Prefer no-key tools first. "
        "Every response includes source metadata for citation and freshness checks."
    ),
)


def envelope(source_id: str, data: Any, *, upstream: Any | None = None) -> dict[str, Any]:
    result = {
        "data": data,
        "source": source_metadata(source_id),
        "retrieved_at": utc_now_iso(),
    }
    if upstream is not None:
        result["upstream"] = upstream
    return result


@mcp.tool
def health_check() -> dict[str, Any]:
    """Return server health and source registry status."""
    return {
        "status": "ok",
        "server": "OpenUKPublicDataMCP",
        "source_count": len(SOURCES),
        "retrieved_at": utc_now_iso(),
    }


@mcp.tool
def list_sources(auth: Literal["all", "none", "optional_key", "required_key"] = "all") -> dict[str, Any]:
    """List configured UK public-data sources and their auth/licence metadata."""
    sources = [source.to_dict() for source in SOURCES.values() if auth == "all" or source.auth == auth]
    return {"sources": sources, "count": len(sources), "retrieved_at": utc_now_iso()}


@mcp.tool
async def lookup_postcode(postcode: str) -> dict[str, Any]:
    """Look up a UK postcode and return location/geography metadata."""
    cleaned = postcode.strip()
    payload = await get_json(f"https://api.postcodes.io/postcodes/{quote(cleaned)}")
    result = payload.get("result") or {}
    data = {
        "postcode": result.get("postcode"),
        "country": result.get("country"),
        "region": result.get("region"),
        "admin_district": result.get("admin_district"),
        "parliamentary_constituency": result.get("parliamentary_constituency_2024") or result.get("parliamentary_constituency"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "codes": result.get("codes"),
    }
    return envelope("postcodes_io", data, upstream=payload)


@mcp.tool
async def get_bank_holidays(
    region: Literal["england-and-wales", "scotland", "northern-ireland"] = "england-and-wales",
) -> dict[str, Any]:
    """Get bank holidays for England and Wales, Scotland, or Northern Ireland."""
    payload = await get_json("https://www.gov.uk/bank-holidays.json")
    region_payload = payload.get(region, {})
    data = {
        "region": region,
        "division": region_payload.get("division"),
        "events": region_payload.get("events", []),
    }
    return envelope("govuk_bank_holidays", data, upstream={region: region_payload})


@mcp.tool
async def get_carbon_intensity(region_id: int | None = None) -> dict[str, Any]:
    """Get current GB carbon intensity, optionally for a regional intensity region ID."""
    if region_id is None:
        url = "https://api.carbonintensity.org.uk/intensity"
    else:
        url = f"https://api.carbonintensity.org.uk/regional/regionid/{region_id}"
    payload = await get_json(url)
    return envelope("carbon_intensity", payload.get("data"), upstream=payload)


@mcp.tool
async def search_govuk(query: str, limit: int = 5) -> dict[str, Any]:
    """Search GOV.UK content."""
    limit = max(1, min(limit, 50))
    payload = await get_json(
        "https://www.gov.uk/api/search.json",
        params={"q": query, "count": limit},
    )
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
    return envelope(
        "govuk_search",
        {"query": query, "total": payload.get("total"), "results": results},
        upstream={"total": payload.get("total")},
    )


@mcp.tool
async def search_public_datasets(query: str, limit: int = 5) -> dict[str, Any]:
    """Search data.gov.uk dataset metadata."""
    limit = max(1, min(limit, 50))
    payload = await get_json(
        "https://data.gov.uk/api/action/package_search",
        params={"q": query, "rows": limit},
    )
    result = payload.get("result", {})
    datasets = []
    for item in result.get("results", [])[:limit]:
        datasets.append(
            {
                "title": item.get("title"),
                "name": item.get("name"),
                "notes": item.get("notes"),
                "metadata_modified": item.get("metadata_modified"),
                "licence": item.get("license_title"),
                "organisation": (item.get("organization") or {}).get("title"),
                "url": f"https://www.data.gov.uk/dataset/{item.get('name')}" if item.get("name") else None,
            }
        )
    return envelope(
        "data_gov_uk",
        {"query": query, "total": result.get("count"), "results": datasets},
        upstream={"success": payload.get("success"), "count": result.get("count")},
    )


def main() -> None:
    mcp.run(show_banner=False, log_level="WARNING")


if __name__ == "__main__":
    main()
