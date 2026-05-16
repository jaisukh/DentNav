"""Calendly API client — all calls are per-doctor using their PAT."""

from datetime import datetime, timezone

import httpx

_BASE = "https://api.calendly.com"
_TIMEOUT = 10.0


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")


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
        "start_time": _fmt(start_time),
        "end_time": _fmt(end_time),
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.get(
            f"{_BASE}/event_type_available_times",
            headers={"Authorization": f"Bearer {pat}"},
            params=params,
        )
        r.raise_for_status()
        return r.json().get("collection", [])


async def create_scheduled_event(
    event_type_uri: str,
    pat: str,
    start_time: datetime,
    end_time: datetime,
    invitee_name: str,
    invitee_email: str,
) -> tuple[str, str]:
    """
    Creates a Calendly scheduled event and returns (event_uri, cancel_url).

    Requires a Calendly Teams or Enterprise plan — the PAT must have the
    scheduled_events:write scope.  Calendly sends confirmation emails with
    the meeting link to both the doctor and the invitee automatically.
    """
    headers = {"Authorization": f"Bearer {pat}"}
    payload = {
        "start_time": _fmt(start_time),
        "end_time": _fmt(end_time),
        "event_type": event_type_uri,
        "invitees": [{"name": invitee_name, "email": invitee_email}],
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(
            f"{_BASE}/scheduled_events",
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
        event_uri: str = r.json()["resource"]["uri"]
        event_uuid = event_uri.rsplit("/", 1)[-1]

        inv_r = await client.get(
            f"{_BASE}/scheduled_events/{event_uuid}/invitees",
            headers=headers,
        )
        inv_r.raise_for_status()
        collection = inv_r.json().get("collection", [])
        cancel_url: str = collection[0]["cancel_url"] if collection else ""

    return event_uri, cancel_url
