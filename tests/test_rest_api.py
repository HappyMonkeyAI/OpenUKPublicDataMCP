"""REST API smoke tests (no live HTTP)."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from openukpublicdata_mcp.rest_api import app


@pytest.mark.asyncio
async def test_api_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_api_explorer_topics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/explorer/topics")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 5
    assert any(topic["id"] == "economy" for topic in body["topics"])


@pytest.mark.asyncio
async def test_api_geo_regions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/geo/regions")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 10