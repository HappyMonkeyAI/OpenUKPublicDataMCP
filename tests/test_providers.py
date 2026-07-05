from openukpublicdata_mcp.providers.os_places import find_places
from openukpublicdata_mcp.providers.tfl import line_status
from openukpublicdata_mcp.server import companies_house_company_profile


async def test_companies_house_auth_required_without_key(monkeypatch):
    monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)
    result = await companies_house_company_profile("00445790")
    assert result["data"]["status"] == "auth_required"
    assert result["source"]["auth"] == "optional_key"


async def test_os_places_auth_required_without_key(monkeypatch):
    monkeypatch.delenv("OS_PLACES_API_KEY", raising=False)
    data, _ = await find_places("SW1A 1AA")
    assert data["status"] == "auth_required"


async def test_tfl_auth_required_without_keys(monkeypatch):
    monkeypatch.delenv("TFL_APP_ID", raising=False)
    monkeypatch.delenv("TFL_APP_KEY", raising=False)
    data, _ = await line_status()
    assert data["status"] == "auth_required"