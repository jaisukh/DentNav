"""Calendly API client — all calls are per-doctor using their PAT."""

from datetime import datetime, timezone

import httpx

_BASE = "https://api.calendly.com"
_TIMEOUT = 10.0


async def get_available_slots(
    event_type_uri: str,
    pat: str,
    start_time: datetime,
    end_time: datetime,
) -> list[dict]:
    """
    Returns raw Calendly available-time objects for the given event type and window.
    Each object has at minimum: start_time (ISO8601), status ("available").
    """
    params = {
        "event_type": event_type_uri,
        "start_time": start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
        "end_time": end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.get(
            f"{_BASE}/event_type_available_times",
            headers={"Authorization": f"Bearer {pat}"},
            params=params,
        )
        r.raise_for_status()
        return r.json().get("collection", [])
