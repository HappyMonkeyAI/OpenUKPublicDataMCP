# Live smoke commands (OpenUKPublicDataMCP)

Run from repo root with venv active:

```bash
cd /home/stephen/projects/OpenUKPublicDataMCP
. .venv/bin/activate
MCP=src/openukpublicdata_mcp/server.py
```

## Health & planning

```bash
fastmcp call $MCP health_check --json
fastmcp call $MCP list_sources auth=none --json
fastmcp call $MCP plan_uk_public_data_research topic='UK economy Q2 2026' period='Q2 2026' depth=standard --json
```

## No-key lookups

```bash
fastmcp call $MCP lookup_postcode postcode='SW1A 1AA' --json
fastmcp call $MCP get_carbon_intensity --json
fastmcp call $MCP search_govuk query='GDP quarterly estimate 2026' limit=3 --json
fastmcp call $MCP search_public_datasets query='UK economy quarterly 2026' limit=3 --json
```

## ONS (post task-003)

```bash
fastmcp call $MCP search_ons_datasets query='consumer price inflation' limit=5 --json
fastmcp call $MCP get_ons_dataset dataset_id='cpih01' --json
fastmcp call $MCP get_ons_latest_version dataset_id='cpih01' --json
fastmcp call $MCP get_ons_observations dataset_id='cpih01' limit=20 --json
```

## Flood (post task-002)

```bash
fastmcp call $MCP list_flood_warnings limit=5 --json
fastmcp call $MCP search_flood_areas query='Thames' limit=3 --json
```

## Planning (post task-009)

```bash
fastmcp call $MCP search_planning_applications limit=3 --json
fastmcp call $MCP search_planning_applications reference='23/00002/FUL' limit=1 --json
```

## Optional key

```bash
# Without key — expect data.status auth_required
fastmcp call $MCP companies_house_company_profile company_number='00445790' --json

# With key in environment
export COMPANIES_HOUSE_API_KEY='your-key'
fastmcp call $MCP companies_house_company_profile company_number='00445790' --json
```

## Inspect

```bash
fastmcp inspect $MCP
fastmcp list $MCP --json
```

## DynamicMCPProxy

After appending `integrations/dynamic-mcp-proxy-user-catalogue-entry.json` to `~/projects/DynamicMCPProxy/user.catalogue.json`:

```bash
cd ~/projects/DynamicMCPProxy
fastmcp call src/dynamic_mcp_proxy/server.py proxy_handshake \
  tech_stack='["uk","python","research"]' \
  task_description='UK quarterly public data executive brief' --json
```
