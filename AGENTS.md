# AGENTS — OpenUKPublicDataMCP

This repo uses Stephen's lightweight multi-agent coordination workflow for complex builds.

## First actions

1. Read `CONTEXT.md`, `HERMES.md`, and relevant ADRs.
2. Check the task board:
   ```bash
   python3 scripts/tasks.py list
   ```
3. Check lock state:
   ```bash
   python3 scripts/update-status.py
   cat .agent-status.md
   ```
4. Claim one unblocked task:
   ```bash
   AGENT_ID=<agent-name> python3 scripts/tasks.py claim <task-id>
   ```
5. Lock files before editing:
   ```bash
   AGENT_ID=<agent-name> python3 scripts/lock.py <file1> <file2> "<task>"
   ```

## Coordination rules

- One agent per task.
- Do not edit files you have not locked.
- Do not edit `.agent-manifest.json`, `.agent-status.md`, or `.agent-tasks.json` directly; use scripts.
- If a lock is held by another agent, choose another task.
- Keep changes minimal and focused.
- Update README/CONTEXT/ADR/research notes when implementation decisions change.

## Verification before completion

Run the relevant real checks before marking a task complete. For baseline work:

```bash
pytest
python -m compileall src tests
fastmcp inspect src/openukpublicdata_mcp/server.py:mcp
fastmcp list src/openukpublicdata_mcp/server.py --json
```

Then complete/unlock:

```bash
AGENT_ID=<agent-name> python3 scripts/tasks.py verify-complete <task-id>
AGENT_ID=<agent-name> python3 scripts/unlock.py <file1> <file2>
```

## CLI swarm options

Hermes may coordinate direct CLI agents where useful: `grok`, `opencode`, `agy`, and other available coding CLIs. Give each a scoped task from `.agent-tasks.json` and require it to follow this file.
