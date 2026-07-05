"""UK Parliament Members API (open, no API key)."""

from __future__ import annotations

from typing import Any

from openukpublicdata_mcp.http import get_json

BASE = "https://members-api.parliament.uk/api"


def _norm_member(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("value") or item
    party = (value.get("latestParty") or {}) if isinstance(value.get("latestParty"), dict) else {}
    house = value.get("latestHouseMembership") or {}
    return {
        "id": value.get("id"),
        "name": value.get("nameDisplayAs") or value.get("nameFullTitle"),
        "party": party.get("name"),
        "constituency": house.get("membershipFrom"),
        "house": "Commons" if house.get("house") == 1 else ("Lords" if house.get("house") == 2 else house.get("house")),
        "thumbnail_url": value.get("thumbnailUrl"),
    }


def _norm_constituency(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("value") or item
    rep = value.get("currentRepresentation") or {}
    member = (rep.get("member") or {}).get("value") if isinstance(rep.get("member"), dict) else None
    out: dict[str, Any] = {
        "id": value.get("id"),
        "name": value.get("name"),
        "start_date": value.get("startDate"),
    }
    if member:
        out["current_mp"] = _norm_member({"value": member})
    return out


async def search_members_by_postcode(postcode: str) -> tuple[dict[str, Any], dict[str, Any]]:
    pc = postcode.strip().replace(" ", "")
    payload = await get_json(f"{BASE}/Members/Search", params={"Postcode": pc})
    items = payload.get("items") or []
    members = [_norm_member(i) for i in items if isinstance(i, dict)]
    return (
        {"postcode": postcode.strip(), "count": len(members), "members": members},
        {"endpoint": f"{BASE}/Members/Search", "postcode": pc},
    )


async def search_constituencies(search_text: str, *, limit: int = 10) -> tuple[dict[str, Any], dict[str, Any]]:
    limit = max(1, min(limit, 20))
    payload = await get_json(
        f"{BASE}/Location/Constituency/Search",
        params={"searchText": search_text.strip(), "skip": 0, "take": limit},
    )
    items = payload.get("items") or []
    rows = [_norm_constituency(i) for i in items if isinstance(i, dict)]
    return (
        {"search_text": search_text.strip(), "count": len(rows), "constituencies": rows[:limit]},
        {"endpoint": f"{BASE}/Location/Constituency/Search"},
    )