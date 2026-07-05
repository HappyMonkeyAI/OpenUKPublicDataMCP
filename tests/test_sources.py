from openukpublicdata_mcp.sources import SOURCES, source_metadata


def test_core_sources_are_no_key_first():
    assert SOURCES
    assert all(source.auth == "none" for source in SOURCES.values())


def test_source_metadata_is_json_safe():
    metadata = source_metadata("govuk_search")
    assert metadata["name"] == "GOV.UK Search API"
    assert metadata["official"] is True
