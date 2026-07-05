from openukpublicdata_mcp.sources import SOURCES, source_metadata


def test_core_sources_are_no_key_first():
    no_key = [s for s in SOURCES.values() if s.auth == "none"]
    assert len(no_key) >= 7
    assert "ea_flood_monitoring" in SOURCES
    assert "ons_beta_api" in SOURCES


def test_optional_key_sources_exist():
    assert SOURCES["companies_house"].auth == "optional_key"


def test_source_metadata_is_json_safe():
    metadata = source_metadata("govuk_search")
    assert metadata["name"] == "GOV.UK Search API"
    assert metadata["official"] is True
