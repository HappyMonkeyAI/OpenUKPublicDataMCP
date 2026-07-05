#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
. .venv/bin/activate
pip install -q '.[web]' 2>/dev/null || pip install -q '.[dev,web]'
export OPENUK_WEB_PORT="${OPENUK_WEB_PORT:-8765}"
if [[ ! -d web/node_modules ]]; then
  (cd web && npm install)
fi
if [[ ! -d web/dist ]]; then
  (cd web && npm run build)
fi
echo "API + static UI: http://127.0.0.1:${OPENUK_WEB_PORT}"
exec openukpublicdata-web