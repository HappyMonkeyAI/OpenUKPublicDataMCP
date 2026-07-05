import respx
from httpx import Response

from openukpublicdata_mcp.server import (
    get_ons_dataset,
    get_ons_latest_version,
    get_ons_observations,
    health_check,
    list_flood_warnings,
    list_sources,
    lookup_postcode,
    search_flood_areas,
    search_govuk,
    search_ons_datasets,
    search_planning_applications,
)


def test_health_check():
    result = health_check()
    assert result["status"] == "ok"
    assert result["source_count"] >= 7


def test_list_sources_filters_none():
    result = list_sources("none")
    assert result["count"] >= 5
    assert all(source["auth"] == "none" for source in result["sources"])


@respx.mock
async def test_lookup_postcode_envelope():
    respx.get("https://api.postcodes.io/postcodes/SW1A%201AA").mock(
        return_value=Response(
            200,
            json={
                "status": 200,
                "result": {
                    "postcode": "SW1A 1AA",
                    "country": "England",
                    "region": "London",
                    "admin_district": "Westminster",
                    "parliamentary_constituency_2024": "Cities of London and Westminster",
                    "latitude": 51.50101,
                    "longitude": -0.141563,
                    "codes": {"admin_district": "E09000033"},
                },
            },
        )
    )
    result = await lookup_postcode("SW1A 1AA")
    assert result["data"]["postcode"] == "SW1A 1AA"
    assert result["source"]["id"] == "postcodes_io"
    assert result["retrieved_at"]


@respx.mock
async def test_search_govuk_normalizes_results():
    route = respx.get("https://www.gov.uk/api/search.json").mock(
        return_value=Response(
            200,
            json={
                "total": 1,
                "results": [
                    {
                        "title": "Bank holidays",
                        "link": "/bank-holidays",
                        "description": "UK bank holidays",
                        "public_timestamp": "2025-01-01T00:00:00Z",
                        "content_store_document_type": "calendar",
                        "organisations": [],
                    }
                ],
            },
        )
    )
    result = await search_govuk("bank holidays", limit=1)
    assert route.called
    assert result["data"]["total"] == 1
    assert result["data"]["results"][0]["title"] == "Bank holidays"
    assert result["source"]["official"] is True


@respx.mock
async def test_list_flood_warnings():
    route = respx.get("https://environment.data.gov.uk/flood-monitoring/id/floods").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "@id": "http://example/flood/1",
                        "severity": "Flood warning",
                        "severityLevel": 2,
                        "description": "River rising",
                        "message": "Act now",
                        "timeRaised": "2026-06-01T12:00:00Z",
                        "floodArea": {"notation": "0654", "label": "Test River", "county": "Testshire", "riverOrSea": "Test"},
                    }
                ],
                "meta": {"publisher": "EA"},
            },
        )
    )
    result = await list_flood_warnings(limit=1)
    assert route.called
    assert result["data"]["count"] == 1
    assert result["data"]["warnings"][0]["severity_level"] == 2
    assert result["source"]["id"] == "ea_flood_monitoring"


@respx.mock
async def test_search_flood_areas():
    respx.get("https://environment.data.gov.uk/flood-monitoring/id/floodAreas").mock(
        return_value=Response(
            200,
            json={"items": [{"@id": "http://x", "notation": "0654", "label": "Thames", "county": "Oxfordshire"}]},
        )
    )
    result = await search_flood_areas("Thames", limit=1)
    assert result["data"]["areas"][0]["label"] == "Thames"


@respx.mock
async def test_search_ons_datasets():
    respx.get("https://api.beta.ons.gov.uk/v1/search").mock(
        return_value=Response(
            200,
            json={
                "count": 1,
                "items": [
                    {
                        "id": "cpih01",
                        "title": "CPIH",
                        "description": "Inflation",
                        "release_date": "2026-05-01",
                        "last_updated": "2026-06-01",
                    }
                ],
            },
        )
    )
    result = await search_ons_datasets("inflation", limit=1)
    assert result["data"]["datasets"][0]["id"] == "cpih01"
    assert result["source"]["official"] is True


@respx.mock
async def test_get_ons_dataset():
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01").mock(
        return_value=Response(
            200,
            json={
                "id": "cpih01",
                "title": "CPIH",
                "release_frequency": "monthly",
                "last_updated": "2026-06-01",
                "links": {"editions": {"href": "https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions"}},
            },
        )
    )
    result = await get_ons_dataset("cpih01")
    assert result["data"]["release_frequency"] == "monthly"


@respx.mock
async def test_get_ons_latest_version_resolves_editions_and_versions():
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01").mock(
        return_value=Response(200, json={"id": "cpih01", "title": "CPIH", "description": "Inflation"})
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions").mock(
        return_value=Response(
            200,
            json={
                "count": 1,
                "items": [
                    {
                        "edition": "time-series",
                        "links": {"latest_version": {"id": "67"}},
                    }
                ],
            },
        )
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions").mock(
        return_value=Response(
            200,
            json={
                "count": 2,
                "items": [
                    {"version": 66, "edition": "time-series", "last_updated": "2026-01-01T00:00:00Z"},
                    {
                        "version": 67,
                        "edition": "time-series",
                        "last_updated": "2026-02-01T00:00:00Z",
                        "dimensions": [{"name": "time", "label": "Time", "id": "mmm-yy"}],
                    },
                ],
            },
        )
    )
    result = await get_ons_latest_version("cpih01")
    assert result["data"]["dataset_id"] == "cpih01"
    assert result["data"]["edition"] == "time-series"
    assert result["data"]["version"] == 67
    assert result["data"]["dimensions"][0]["name"] == "time"
    assert result["source"]["id"] == "ons_beta_api"


@respx.mock
async def test_get_ons_observations_auto_resolves_latest_and_limits_results():
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01").mock(
        return_value=Response(200, json={"id": "cpih01", "title": "CPIH"})
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions").mock(
        return_value=Response(
            200,
            json={
                "count": 1,
                "items": [{"edition": "time-series", "links": {"latest_version": {"id": "67"}}}],
            },
        )
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions").mock(
        return_value=Response(
            200,
            json={"count": 1, "items": [{"version": 67, "edition": "time-series"}]},
        )
    )
    observations_route = respx.get(
        "https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions/67/observations",
        params={"time": "*"},
    ).mock(
        return_value=Response(
            200,
            json={
                "count": 2,
                "items": [
                    {"observation": "131.4", "dimensions": {"time": {"id": "Feb-26", "label": "Feb 2026"}}},
                    {"observation": "130.2", "dimensions": {"time": {"id": "Jan-26", "label": "Jan 2026"}}},
                ],
            },
        )
    )
    result = await get_ons_observations("cpih01", limit=1)
    assert observations_route.called
    assert result["data"]["edition"] == "time-series"
    assert result["data"]["version"] == 67
    assert result["data"]["query"] == {"time": "*"}
    assert result["data"]["count"] == 1
    assert result["data"]["observations"][0]["observation"] == "131.4"


@respx.mock
async def test_search_planning_applications_envelope():
    respx.get("https://www.planning.data.gov.uk/entity.json").mock(
        return_value=Response(
            200,
            json={
                "count": 1,
                "entities": [
                    {
                        "entity": 10000000000,
                        "reference": "23/00002/FUL",
                        "description": "Single storey extension",
                        "decision-date": "2023-05-09",
                        "dataset": "planning-application",
                    }
                ],
            },
        )
    )
    result = await search_planning_applications(limit=1)
    assert result["data"]["applications"][0]["reference"] == "23/00002/FUL"
    assert result["source"]["id"] == "planning_data_gov_uk"
    assert result["retrieved_at"]
