"""ONS Beta API adapters."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from openukpublicdata_mcp.http import get_json

BASE_URL = "https://api.beta.ons.gov.uk/v1"
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
    payload = await get_json(f"{BASE_URL}/datasets/{quote(cleaned)}")
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


def _version_value(item: dict[str, Any]) -> int:
    candidate = item.get("version") or item.get("id") or (item.get("links", {}).get("self", {}).get("id"))
    try:
        return int(candidate)
    except (TypeError, ValueError):
        return 0


def _normalise_version(
    dataset_id: str,
    edition: str,
    version_item: dict[str, Any],
) -> dict[str, Any]:
    version = _version_value(version_item)
    return {
        "dataset_id": dataset_id,
        "edition": edition,
        "version": version,
        "version_url": f"{BASE_URL}/datasets/{quote(dataset_id)}/editions/{quote(edition)}/versions/{version}" if version else None,
        "last_updated": version_item.get("last_updated"),
        "release_date": version_item.get("release_date"),
        "state": version_item.get("state"),
        "dimensions": [
            {
                "name": dimension.get("name"),
                "label": dimension.get("label"),
                "id": dimension.get("id"),
            }
            for dimension in version_item.get("dimensions", [])
        ],
        "downloads": version_item.get("downloads"),
    }


async def resolve_latest_version(dataset_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve the latest published ONS dataset edition and version."""
    cleaned = dataset_id.strip()
    quoted_id = quote(cleaned)
    dataset_payload = await get_json(f"{BASE_URL}/datasets/{quoted_id}")
    editions_payload = await get_json(f"{BASE_URL}/datasets/{quoted_id}/editions")
    editions = editions_payload.get("items", [])
    edition_item = next(
        (item for item in editions if item.get("links", {}).get("latest_version", {}).get("id")),
        editions[0] if editions else {},
    )
    edition = edition_item.get("edition") or "time-series"
    versions_payload = await get_json(f"{BASE_URL}/datasets/{quoted_id}/editions/{quote(edition)}/versions")
    versions = versions_payload.get("items", [])
    if versions:
        version_item = max(versions, key=_version_value)
    else:
        version_id = edition_item.get("links", {}).get("latest_version", {}).get("id")
        version_item = {"version": version_id}

    data = _normalise_version(cleaned, edition, version_item)
    data["title"] = dataset_payload.get("title")
    data["description"] = dataset_payload.get("description")
    upstream = {
        "dataset": {"id": dataset_payload.get("id"), "latest_version": dataset_payload.get("links", {}).get("latest_version")},
        "editions_count": editions_payload.get("count", len(editions)),
        "versions_count": versions_payload.get("count", len(versions)),
    }
    return data, upstream


async def _first_dimension_option(dataset_id: str, edition: str, version: int | str, dimension: str) -> str | None:
    options_payload = await get_json(
        f"{BASE_URL}/datasets/{quote(dataset_id)}/editions/{quote(edition)}/versions/{quote(str(version))}"
        f"/dimensions/{quote(dimension)}/options",
        params={"limit": 1},
    )
    items = options_payload.get("items", [])
    if not items:
        return None
    return items[0].get("option")


async def _observation_query_params(
    dataset_id: str,
    edition: str,
    version: int | str,
    dimensions: list[dict[str, Any]],
) -> dict[str, str]:
    params = {"time": "*"}
    for dimension in dimensions:
        name = dimension.get("name")
        if not name or name == "time":
            continue
        option = await _first_dimension_option(dataset_id, edition, version, name)
        if option:
            params[name] = option
    return params


async def get_observations(
    dataset_id: str,
    edition: str | None = None,
    version: int | str | None = None,
    limit: int = 20,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fetch ONS observations using the minimal time=* query, resolving latest edition/version when omitted."""
    cleaned = dataset_id.strip()
    resolved: dict[str, Any] | None = None
    upstream: dict[str, Any] = {}
    if edition is None or version is None:
        resolved, resolve_upstream = await resolve_latest_version(cleaned)
        upstream["resolution"] = resolve_upstream
        edition = edition or resolved["edition"]
        version = version or resolved["version"]

    quoted_id = quote(cleaned)
    quoted_edition = quote(str(edition))
    quoted_version = quote(str(version))
    if resolved is None:
        version_payload = await get_json(f"{BASE_URL}/datasets/{quoted_id}/editions/{quoted_edition}/versions/{quoted_version}")
        dimensions = version_payload.get("dimensions", [])
        upstream["version"] = {"id": version_payload.get("id"), "version": version_payload.get("version")}
    else:
        dimensions = resolved.get("dimensions", [])
    params = await _observation_query_params(cleaned, str(edition), version, dimensions)
    payload = await get_json(
        f"{BASE_URL}/datasets/{quoted_id}/editions/{quoted_edition}/versions/{quoted_version}/observations",
        params=params,
    )
    items = payload.get("observations") or payload.get("items") or []
    limited_items = items[:limit]
    observations = []
    for item in limited_items:
        observations.append(
            {
                "observation": item.get("observation") or item.get("value"),
                "dimensions": item.get("dimensions"),
                "metadata": item.get("metadata"),
            }
        )
    data = {
        "dataset_id": cleaned,
        "edition": edition,
        "version": int(version) if str(version).isdigit() else version,
        "query": params,
        "count": len(observations),
        "observations": observations,
    }
    if resolved is not None:
        data["resolved_latest"] = resolved
    upstream["observations"] = {
        "count": payload.get("count", len(items)),
        "total_count": payload.get("total_count"),
        "offset": payload.get("offset"),
        "limit": payload.get("limit"),
    }
    return data, upstream
