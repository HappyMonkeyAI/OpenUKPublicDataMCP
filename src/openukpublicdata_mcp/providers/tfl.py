"""TfL Unified API (optional app id + key)."""

from __future__ import annotations

import os
from typing import Any

from openukpublicdata_mcp.http import get_json

BASE = "https://api.tfl.gov.uk"


def tfl_credentials() -> tuple[str | None, str | None]:
    return os.environ.get("TFL_APP_ID"), os.environ.get("TFL_APP_KEY")


async def line_status(*, line_ids: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    app_id, app_key = tfl_credentials()
    if not app_id or not app_key:
        return (
            {
                "status": "auth_required",
                "message": "Set TFL_APP_ID and TFL_APP_KEY for TfL Unified API.",
            },
            {"auth": "missing"},
        )
    params = {"app_id": app_id, "app_key": app_key}
    if line_ids and line_ids.strip():
        path = f"/Line/{line_ids.strip()}/Status"
    else:
        path = "/Line/Mode/tube,overground,dlr,tram/Status"
    payload = await get_json(f"{BASE}{path}", params=params)
    lines = payload if isinstance(payload, list) else [payload]
    return (
        {"line_filter": line_ids, "count": len(lines), "lines": lines},
        {"path": path},
    )