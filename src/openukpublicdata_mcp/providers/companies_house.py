"""Optional-key UK data providers."""

from __future__ import annotations

import base64
import os
from typing import Any

from openukpublicdata_mcp.http import get_json


def companies_house_api_key() -> str | None:
    key = os.environ.get("COMPANIES_HOUSE_API_KEY", "").strip()
    return key or None


async def fetch_company_profile(company_number: str) -> dict[str, Any]:
    """Return profile dict or auth_required payload (never raises for missing key)."""
    key = companies_house_api_key()
    if not key:
        return {
            "status": "auth_required",
            "message": "Set COMPANIES_HOUSE_API_KEY in the MCP server environment to enable Companies House lookups.",
            "company_number": company_number.strip(),
        }
    cleaned = company_number.strip()
    token = base64.b64encode(f"{key}:".encode()).decode()
    payload = await get_json(
        f"https://api.company-information.service.gov.uk/company/{cleaned}",
        headers={"Authorization": f"Basic {token}"},
    )
    return {
        "status": "ok",
        "company_number": cleaned,
        "company_name": payload.get("company_name"),
        "company_status": payload.get("company_status"),
        "date_of_creation": payload.get("date_of_creation"),
        "registered_office_address": payload.get("registered_office_address"),
        "sic_codes": payload.get("sic_codes"),
    }