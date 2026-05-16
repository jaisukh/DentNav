"""Calendly API client — all calls are per-doctor using their PAT."""

from datetime import UTC, datetime

import httpx

_BASE = "https://api.calendly.com"
_TIMEOUT = 10.0


def _fmt(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000000Z")


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


async def create_invitee(
    event_type_uri: str,
    pat: str,
    start_time: datetime,
    invitee_name: str,
    invitee_email: str,
) -> tuple[str, str]:
    """
    Books a Calendly slot via POST /invitees and returns (event_uri, cancel_url).

    Requires a paid Calendly plan (any tier). Works with a standard PAT.
    Calendly automatically sends calendar invites and confirmation emails to
    both the doctor and the invitee.
    """
    payload = {
        "event_type": event_type_uri,
        "start_time": _fmt(start_time),
        "invitee": {
            "name": invitee_name,
            "email": invitee_email,
        },
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(
            f"{_BASE}/invitees",
            headers={"Authorization": f"Bearer {pat}"},
            json=payload,
        )
        r.raise_for_status()
        resource = r.json()["resource"]
        event_uri: str = resource["event"]
        cancel_url: str = resource["cancel_url"]

    return event_uri, cancel_url
