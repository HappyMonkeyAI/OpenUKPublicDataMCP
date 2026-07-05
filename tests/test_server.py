import respx
from httpx import Response

from openukpublicdata_mcp.server import health_check, list_sources, lookup_postcode, search_govuk


def test_health_check():
    result = health_check()
    assert result["status"] == "ok"
    assert result["source_count"] >= 5


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
