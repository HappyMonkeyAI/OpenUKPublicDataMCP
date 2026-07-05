import respx
from httpx import Response

from openukpublicdata_mcp.server import (
    get_ons_dataset,
    health_check,
    list_flood_warnings,
    list_sources,
    lookup_postcode,
    search_flood_areas,
    search_govuk,
    search_ons_datasets,
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
