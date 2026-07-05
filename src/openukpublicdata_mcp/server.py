from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote

from fastmcp import FastMCP

from openukpublicdata_mcp.http import get_json, utc_now_iso
from openukpublicdata_mcp.planning import (
    METHODOLOGY_MD,
    build_research_plan,
    format_plan_markdown,
)
from openukpublicdata_mcp.sources import SOURCES, source_metadata
from openukpublicdata_mcp.steering import cap_envelope

mcp = FastMCP(
    "OpenUKPublicDataMCP",
    instructions=(
        "UK public data MCP. Start with list_sources(auth='none') and plan_uk_public_data_research "
        "before broad discovery. Prefer no-key tools. Every tool response includes source metadata "
        "for citation; preserve source and retrieved_at in summaries."
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
    return cap_envelope(result)


def _slugify(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return slug[:48] or "topic"


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


@mcp.tool
async def list_flood_warnings(limit: int = 10) -> dict[str, Any]:
    """List current Environment Agency flood warnings (England)."""
    limit = max(1, min(limit, 50))
    payload = await get_json(
        "https://environment.data.gov.uk/flood-monitoring/id/floods",
        params={"_limit": limit},
    )
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
    return envelope(
        "ea_flood_monitoring",
        {"count": len(items), "warnings": items},
        upstream={"meta": payload.get("meta")},
    )


@mcp.tool
async def search_flood_areas(query: str, limit: int = 5) -> dict[str, Any]:
    """Search Environment Agency flood monitoring areas by name or river."""
    limit = max(1, min(limit, 20))
    payload = await get_json(
        "https://environment.data.gov.uk/flood-monitoring/id/floodAreas",
        params={"search": query, "_limit": limit},
    )
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
    return envelope(
        "ea_flood_monitoring",
        {"query": query, "count": len(areas), "areas": areas},
        upstream={"meta": payload.get("meta")},
    )


@mcp.tool
async def search_ons_datasets(query: str, limit: int = 10) -> dict[str, Any]:
    """Search ONS Beta API datasets by keyword."""
    limit = max(1, min(limit, 50))
    payload = await get_json(
        "https://api.beta.ons.gov.uk/v1/search",
        params={"q": query, "size": limit},
    )
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
    return envelope(
        "ons_beta_api",
        {"query": query, "count": len(datasets), "datasets": datasets},
        upstream={"count": payload.get("count")},
    )


@mcp.tool
async def get_ons_dataset(dataset_id: str) -> dict[str, Any]:
    """Fetch ONS dataset metadata (release frequency, editions, links)."""
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
    return envelope("ons_beta_api", data, upstream={"id": payload.get("id")})


@mcp.tool
def plan_uk_public_data_research(
    topic: str,
    depth: Literal["quick", "standard", "deep"] = "standard",
    period: str | None = None,
) -> dict[str, Any]:
    """Return a structured research plan (tool order, depth, suggested output) for UK public-data questions."""
    plan = build_research_plan(topic, depth=depth, period=period)
    plan["plan_markdown"] = format_plan_markdown(plan)
    return plan


@mcp.tool
def get_research_methodology() -> str:
    """Methodology for no-key-first UK public data research and citation rules."""
    return METHODOLOGY_MD


@mcp.tool
def save_uk_research_note(
    topic: str,
    content_markdown: str,
    slug: str | None = None,
    filename: str = "UK_PUBLIC_DATA_BRIEF.md",
) -> dict[str, Any]:
    """Persist a research brief under ~/research/<slug>/ (or UK_RESEARCH_ROOT)."""
    research_root = Path(os.environ.get("UK_RESEARCH_ROOT", Path.home() / "research"))
    use_slug = slug or _slugify(topic)
    out_dir = (research_root / use_slug).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    header = f"# {topic}\n\n_Saved by OpenUKPublicDataMCP_\n\n"
    out_path.write_text(header + content_markdown.strip() + "\n", encoding="utf-8")
    return {"path": str(out_path), "slug": use_slug, "bytes": out_path.stat().st_size}


@mcp.resource("openuk://methodology")
async def methodology_resource() -> str:
    return METHODOLOGY_MD


def main() -> None:
    mcp.run(show_banner=False, log_level="WARNING")


if __name__ == "__main__":
    main()
