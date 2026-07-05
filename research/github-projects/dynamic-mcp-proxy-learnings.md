# DynamicMCPProxy → OpenUKPublicDataMCP learnings

Local reference: `/home/stephen/projects/DynamicMCPProxy`

## Already aligned

| Proxy lesson | OpenUK status |
|--------------|---------------|
| [S-01] stdout sacred, `show_banner=False` | `server.py` uses `log_level="WARNING"` |
| [S-03] underscore tool names | All tools use underscores |
| Source registry + citations | `sources.py` + `envelope()` |
| Thin docs / CONTEXT / research | Present from bootstrap |

## Adopted in this repo

1. **Planning surface** (from `article-research-mcp` + proxy discovery model)
   - `plan_uk_public_data_research`
   - `get_research_methodology`
   - Resource `openuk://methodology`
2. **Response steering** ([S-12])
   - `steering.cap_envelope()` on tool returns
   - Catalogue `pick` + `token_budget` in `integrations/dynamic-mcp-proxy-user-catalogue-entry.json`
3. **Proxy registration**
   - Copy JSON entry into `DynamicMCPProxy/user.catalogue.json` (gitignored overlay)

## Next (high value)

| Learning | Action |
|----------|--------|
| Thin adapters | Move HTTP per source to `src/openukpublicdata_mcp/sources/*.py` |
| ONS tools (task-003) | Stops GOV.UK search-only quarterly briefs |
| MCP prompt `suggest_uk_data_tools` | Mirror proxy `suggest_tools_for_context` |
| Optional receipts | JSONL audit of tool calls (proxy `guardrails.py`) |
| REST bridge ([S-14]) | Declarative ONS/OpenAPI via 40mcp-style config — only if tool count explodes |

## Do not copy blindly

- **Lazy mount / tool budget** — proxy concern; single-purpose server stays small.
- **JWT auth** — only if exposing HTTP deployment publicly.
- **Full guardrails stack** — start with truncation; add rate limits when HTTP multi-tenant.

## Register in DynamicMCPProxy

```bash
# Append integrations/dynamic-mcp-proxy-user-catalogue-entry.json to:
# ~/projects/DynamicMCPProxy/user.catalogue.json
# Then proxy_handshake(tech_stack=["uk","python"], task_description="UK public data quarterly brief")
```