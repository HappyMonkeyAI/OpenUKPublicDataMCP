from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

USER_AGENT = "OpenUKPublicDataMCP/0.1 (+https://github.com/SPhillips1337/OpenUKPublicDataMCP)"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpstreamError(RuntimeError):
    pass


async def get_json(url: str, *, params: dict[str, Any] | None = None, timeout: float = 20.0) -> Any:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise UpstreamError(f"HTTP {exc.response.status_code} from {url}") from exc
        except httpx.HTTPError as exc:
            raise UpstreamError(f"HTTP error from {url}: {exc.__class__.__name__}") from exc
        except ValueError as exc:
            raise UpstreamError(f"Invalid JSON from {url}") from exc
