import respx
from httpx import Response

from openukpublicdata_mcp.server import (
    get_cpih_inflation_headline,
    get_ons_dataset,
    get_ons_latest_version,
    get_ons_observations,
    health_check,
    list_flood_warnings,
    list_sources,
    list_uk_regions,
    lookup_postcode,
    police_street_crime_near,
    search_flood_areas,
    search_govuk,
    search_mp_by_postcode,
    search_ons_datasets,
    search_planning_applications,
    search_constituencies,
    met_office_site_forecast,
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


def test_list_uk_regions_envelope():
    result = list_uk_regions()
    assert result["data"]["count"] >= 10
    assert result["data"]["regions"][0]["sample_postcode"]


@respx.mock
async def test_get_cpih_inflation_headline():
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01").mock(
        return_value=Response(200, json={"id": "cpih01", "title": "CPIH"})
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions").mock(
        return_value=Response(200, json={"items": [{"edition": "time-series", "links": {"latest_version": {"id": "67"}}}]})
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions").mock(
        return_value=Response(200, json={"items": [{"version": 67}]})
    )
    respx.get("https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions/67").mock(
        return_value=Response(
            200,
            json={
                "version": 67,
                "dimensions": [
                    {"name": "time", "label": "Time"},
                    {"name": "aggregate", "label": "Aggregate"},
                ],
            },
        )
    )
    respx.get(
        "https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions/67/dimensions/aggregate/options"
    ).mock(return_value=Response(200, json={"items": [{"option": "cpih1dim1A0"}]}))
    respx.get(
        "https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions/67/observations"
    ).mock(
        return_value=Response(
            200,
            json={
                "observations": [
                    {"observation": "130.0", "dimensions": {"time": {"id": "Dec-25"}}},
                    {"observation": "131.4", "dimensions": {"time": {"id": "Jan-26"}}},
                ]
            },
        )
    )
    result = await get_cpih_inflation_headline("cpih01")
    assert result["data"]["month_on_month_percent"] is not None
    assert result["data"]["latest_period"] == "Jan-26"


@respx.mock
async def test_police_street_crime_near():
    respx.get("https://data.police.uk/api/crimes-street/all-crime").mock(
        return_value=Response(
            200,
            json=[{"category": "violent-crime", "month": "2024-01", "location": {"latitude": "52.6", "longitude": "-1.1"}}],
        )
    )
    result = await police_street_crime_near(52.6, -1.1, limit=5)
    assert result["data"]["count"] == 1
    assert result["source"]["id"] == "police_uk"


@respx.mock
async def test_search_mp_by_postcode():
    respx.get("https://members-api.parliament.uk/api/Members/Search").mock(
        return_value=Response(
            200,
            json={
                "items": [
                    {
                        "value": {
                            "id": 1,
                            "nameDisplayAs": "Test MP",
                            "latestParty": {"name": "Independent"},
                            "latestHouseMembership": {"membershipFrom": "Testshire", "house": 1},
                        }
                    }
                ]
            },
        )
    )
    result = await search_mp_by_postcode("SW1A 1AA")
    assert result["data"]["members"][0]["name"] == "Test MP"
    assert result["source"]["id"] == "parliament_uk"


@respx.mock
async def test_search_constituencies():
    respx.get("https://members-api.parliament.uk/api/Location/Constituency/Search").mock(
        return_value=Response(200, json={"items": [{"value": {"id": 99, "name": "Richmond and Northallerton"}}]})
    )
    result = await search_constituencies("Richmond", limit=5)
    assert result["data"]["constituencies"][0]["name"] == "Richmond and Northallerton"


async def test_met_office_site_forecast_auth_required(monkeypatch):
    monkeypatch.delenv("MET_OFFICE_DATAHUB_API_KEY", raising=False)
    monkeypatch.delenv("MET_OFFICE_API_KEY", raising=False)
    result = await met_office_site_forecast(51.5, -0.12)
    assert result["data"]["status"] == "auth_required"
