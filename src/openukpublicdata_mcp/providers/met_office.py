"""Met Office Weather DataHub — site-specific forecast (optional API key).

DataPoint retired 2024; use Weather DataHub Global Spot (free tier: register at datahub.metoffice.gov.uk).
"""

from __future__ import annotations

import os
from typing import Any

from openukpublicdata_mcp.http import get_json

# Documented host used by integrations (see Met Office DataHub site-specific docs)
HOURLY_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
DAILY_URL = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/daily"


def met_office_api_key() -> str | None:
    return os.environ.get("MET_OFFICE_DATAHUB_API_KEY") or os.environ.get("MET_OFFICE_API_KEY") or None


def _auth_block(latitude: float, longitude: float) -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "status": "auth_required",
            "message": (
                "Register at https://datahub.metoffice.gov.uk/, subscribe to Global Spot (free tier), "
                "then set MET_OFFICE_DATAHUB_API_KEY."
            ),
            "latitude": latitude,
            "longitude": longitude,
        },
        {"auth": "missing"},
    )


async def site_forecast(
    latitude: float,
    longitude: float,
    *,
    resolution: str = "hourly",
) -> tuple[dict[str, Any], dict[str, Any]]:
    key = met_office_api_key()
    if not key:
        return _auth_block(latitude, longitude)

    resolution = (resolution or "hourly").lower()
    url = HOURLY_URL if resolution == "hourly" else DAILY_URL
    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "datasource": "BD1",
        "includeLocationName": "true",
        "excludeParameterMetadata": "true",
    }
    payload = await get_json(url, params=params, headers={"apikey": key})
    features = payload.get("features") or []
    props = (features[0].get("properties") if features else {}) or {}
    return (
        {
            "latitude": latitude,
            "longitude": longitude,
            "resolution": resolution,
            "location_name": props.get("locationName"),
            "model_run_date": props.get("modelRunDate"),
            "forecast": props.get("timeSeries") or props.get("values") or props,
            "feature_count": len(features),
        },
        {"endpoint": url, "resolution": resolution},
    )