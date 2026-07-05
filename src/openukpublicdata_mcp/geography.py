"""UK geography metadata for web explorer (centroids + drill-down labels)."""

from __future__ import annotations

from typing import Any

# Parliamentary constituencies sample + UK regions/nations for map drill-down.
# Full boundary GeoJSON is served from web/public/geo/.

REGIONS: list[dict[str, Any]] = [
    {
        "id": "london",
        "name": "London",
        "type": "region",
        "sample_postcode": "SW1A 1AA",
        "lat": 51.501,
        "lng": -0.142,
    },
    {
        "id": "north-west",
        "name": "North West",
        "type": "region",
        "sample_postcode": "M1 1AE",
        "lat": 53.48,
        "lng": -2.24,
    },
    {
        "id": "north-east",
        "name": "North East",
        "type": "region",
        "sample_postcode": "NE1 4LP",
        "lat": 54.97,
        "lng": -1.61,
    },
    {
        "id": "yorkshire-and-the-humber",
        "name": "Yorkshire and The Humber",
        "type": "region",
        "sample_postcode": "LS1 1UR",
        "lat": 53.8,
        "lng": -1.55,
    },
    {
        "id": "east-midlands",
        "name": "East Midlands",
        "type": "region",
        "sample_postcode": "NG1 1AA",
        "lat": 52.95,
        "lng": -1.15,
    },
    {
        "id": "west-midlands",
        "name": "West Midlands",
        "type": "region",
        "sample_postcode": "B1 1TT",
        "lat": 52.48,
        "lng": -1.9,
    },
    {
        "id": "east-of-england",
        "name": "East of England",
        "type": "region",
        "sample_postcode": "CB2 1TN",
        "lat": 52.2,
        "lng": 0.12,
    },
    {
        "id": "south-east",
        "name": "South East",
        "type": "region",
        "sample_postcode": "BN1 1EE",
        "lat": 50.82,
        "lng": -0.14,
    },
    {
        "id": "south-west",
        "name": "South West",
        "type": "region",
        "sample_postcode": "BS1 4ST",
        "lat": 51.45,
        "lng": -2.59,
    },
    {
        "id": "wales",
        "name": "Wales",
        "type": "nation",
        "sample_postcode": "CF10 1EP",
        "lat": 51.48,
        "lng": -3.18,
    },
    {
        "id": "scotland",
        "name": "Scotland",
        "type": "nation",
        "sample_postcode": "EH1 1YZ",
        "lat": 55.95,
        "lng": -3.19,
    },
    {
        "id": "northern-ireland",
        "name": "Northern Ireland",
        "type": "nation",
        "sample_postcode": "BT1 1AA",
        "lat": 54.6,
        "lng": -5.93,
    },
]


def list_regions() -> dict[str, Any]:
    return {"count": len(REGIONS), "regions": REGIONS}


def get_region(region_id: str) -> dict[str, Any] | None:
    for region in REGIONS:
        if region["id"] == region_id:
            return region
    return None


EXPLORER_TOPICS: list[dict[str, Any]] = [
    {
        "id": "economy",
        "title": "Economy & prices",
        "summary": "ONS datasets, CPIH observations, GOV.UK releases",
        "tools": ["search_ons_datasets", "get_ons_observations", "get_cpih_inflation_headline", "search_govuk"],
    },
    {
        "id": "energy",
        "title": "Energy & climate",
        "summary": "Live grid carbon intensity",
        "tools": ["get_carbon_intensity"],
    },
    {
        "id": "environment",
        "title": "Floods & resilience",
        "summary": "Environment Agency warnings and areas",
        "tools": ["list_flood_warnings", "search_flood_areas"],
    },
    {
        "id": "place",
        "title": "Place & geography",
        "summary": "Postcodes, regions, constituencies",
        "tools": ["lookup_postcode", "list_uk_regions"],
    },
    {
        "id": "planning",
        "title": "Planning (England)",
        "summary": "Planning Data platform applications",
        "tools": ["search_planning_applications"],
    },
    {
        "id": "safety",
        "title": "Street crime (England & Wales)",
        "summary": "Police.uk near a lat/lng point",
        "tools": ["police_street_crime_near"],
    },
    {
        "id": "catalogue",
        "title": "Open data catalogue",
        "summary": "data.gov.uk dataset discovery",
        "tools": ["search_public_datasets"],
    },
]


def explorer_topics() -> dict[str, Any]:
    return {"topics": EXPLORER_TOPICS, "count": len(EXPLORER_TOPICS)}