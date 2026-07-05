from openukpublicdata_mcp.server import companies_house_company_profile


async def test_companies_house_auth_required_without_key(monkeypatch):
    monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)
    result = await companies_house_company_profile("00445790")
    assert result["data"]["status"] == "auth_required"
    assert result["source"]["auth"] == "optional_key"