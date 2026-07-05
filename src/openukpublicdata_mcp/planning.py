from __future__ import annotations

from typing import Any, Literal

Depth = Literal["quick", "standard", "deep"]

METHODOLOGY_MD = """# UK public data research methodology (OpenUKPublicDataMCP)

## Source tiers

1. **Official API, no key** — use first (GOV.UK search, data.gov.uk, postcodes.io, carbon intensity, ONS, EA flood).
2. **Official API, optional key** — only when the user supplies credentials (Companies House, OS, TfL).
3. **Official datasets** — discover via data.gov.uk; fetch releases manually or add a dedicated tool.
4. **Community mirrors** — label as non-official; cite upstream licence.

## Recommended tool order

1. `list_sources(auth="none")` — see what works without keys.
2. `plan_uk_public_data_research` — pick tools for the question.
3. Discovery: `search_govuk`, `search_public_datasets`, `search_ons_datasets`.
4. Point lookups: `lookup_postcode`, `get_bank_holidays`, `get_carbon_intensity`, `get_ons_dataset`.
5. Synthesis: combine envelopes; every fact needs `source` + `retrieved_at`.

## Depth levels

- **quick** — 2–3 tool calls, GOV.UK + one numeric/live source.
- **standard** — discovery + ONS search + 2 domain tools + short markdown brief.
- **deep** — add flood warnings; persist note under `~/research/<slug>/`.

## Citation rule

Never drop `source.official`, `source.licence`, or `retrieved_at` when summarising for a human.
"""


def build_research_plan(
    topic: str,
    *,
    depth: Depth = "standard",
    period: str | None = None,
) -> dict[str, Any]:
    period_hint = period or "unspecified period"
    base_steps = [
        {"step": 1, "action": "list_sources", "args": {"auth": "none"}, "why": "Confirm no-key coverage"},
        {"step": 2, "action": "search_govuk", "args": {"query": topic, "limit": 8}, "why": "Official releases and guidance"},
        {"step": 3, "action": "search_public_datasets", "args": {"query": topic, "limit": 8}, "why": "Dataset catalogue"},
        {"step": 4, "action": "search_ons_datasets", "args": {"query": topic, "limit": 8}, "why": "Official ONS time-series catalogue"},
    ]
    if depth in ("standard", "deep"):
        base_steps.extend(
            [
                {
                    "step": 5,
                    "action": "get_carbon_intensity",
                    "args": {},
                    "why": "Live GB grid signal (energy quarter context)",
                },
                {
                    "step": 6,
                    "action": "lookup_postcode",
                    "args": {"postcode": "SW1A 1AA"},
                    "why": "Smoke-test geodata envelope (optional anchor)",
                },
            ]
        )
    if depth == "deep":
        base_steps.extend(
            [
                {
                    "step": 7,
                    "action": "list_flood_warnings",
                    "args": {"limit": 5},
                    "why": "Environmental risk context (England)",
                },
                {
                    "step": 8,
                    "action": "save_uk_research_note",
                    "args": {"topic": topic, "content_markdown": "<synthesise from tool envelopes>"},
                    "why": "Persist brief under ~/research",
                },
            ]
        )
    return {
        "topic": topic,
        "depth": depth,
        "period": period_hint,
        "methodology": "no-key-first, source-cited envelopes",
        "steps": base_steps,
        "suggested_output": f"One-page markdown brief for: {topic} ({period_hint})",
    }


def format_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# Research plan: {plan['topic']}",
        "",
        f"- Depth: **{plan['depth']}**",
        f"- Period: {plan['period']}",
        f"- Method: {plan['methodology']}",
        "",
        "## Steps",
    ]
    for step in plan["steps"]:
        lines.append(f"{step['step']}. `{step['action']}` — {step['why']}")
    lines.extend(["", "## Target output", "", plan["suggested_output"], ""])
    return "\n".join(lines)