from openukpublicdata_mcp.planning import build_research_plan, format_plan_markdown
from openukpublicdata_mcp.server import get_research_methodology, plan_uk_public_data_research
from openukpublicdata_mcp.steering import cap_envelope


def test_build_research_plan_standard():
    plan = build_research_plan("UK inflation", depth="standard", period="Q2 2026")
    assert plan["topic"] == "UK inflation"
    assert plan["depth"] == "standard"
    assert len(plan["steps"]) >= 4
    assert any(s["action"] == "search_govuk" for s in plan["steps"])


def test_format_plan_markdown():
    plan = build_research_plan("energy", depth="quick")
    md = format_plan_markdown(plan)
    assert "# Research plan: energy" in md
    assert "list_sources" in md


def test_plan_tool_exposes_markdown():
    out = plan_uk_public_data_research("migration statistics", period="past quarter")
    assert "plan_markdown" in out
    assert "migration statistics" in out["plan_markdown"]


def test_methodology_non_empty():
    assert "Source tiers" in get_research_methodology()


def test_cap_envelope_truncates_large_list():
    big = {"data": [{"x": i} for i in range(100)], "source": {"id": "t"}, "retrieved_at": "now"}
    capped = cap_envelope(big, max_chars=500)
    assert capped.get("data_truncated") is True
    assert len(capped["data"]) == 5