from __future__ import annotations

import json
from typing import Any

# DynamicMCPProxy [S-12]: cap tool payloads before they flood agent context.
DEFAULT_TOKEN_BUDGET_CHARS = 12_000


def cap_envelope(envelope: dict[str, Any], *, max_chars: int = DEFAULT_TOKEN_BUDGET_CHARS) -> dict[str, Any]:
    """Truncate oversized JSON envelopes while preserving source metadata."""
    try:
        encoded = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError):
        return envelope
    if len(encoded) <= max_chars:
        return envelope
    trimmed = dict(envelope)
    upstream = trimmed.pop("upstream", None)
    data = trimmed.get("data")
    if isinstance(data, list) and len(data) > 5:
        trimmed["data"] = data[:5]
        trimmed["data_truncated"] = True
        trimmed["data_original_count"] = len(data)
    elif isinstance(data, dict) and len(json.dumps(data)) > max_chars // 2:
        trimmed["data"] = {"summary": "payload truncated", "keys": list(data.keys())[:20]}
        trimmed["data_truncated"] = True
    if upstream is not None:
        trimmed["upstream"] = {"present": True, "omitted": True}
    trimmed["steering"] = {"token_budget_chars": max_chars, "truncated": True}
    return trimmed