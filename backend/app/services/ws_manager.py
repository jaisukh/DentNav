"""In-memory WebSocket connection manager for real-time slot availability updates."""

from collections import defaultdict

from fastapi import WebSocket


class SlotConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, doctor_service_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[doctor_service_id].add(ws)

    def disconnect(self, doctor_service_id: str, ws: WebSocket) -> None:
        self._connections[doctor_service_id].discard(ws)

    async def broadcast(self, doctor_service_id: str, slot_time: str, status: str) -> None:
        """Push a slot status change to all clients watching this doctor_service_id."""
        payload = {"type": "slot_update", "slot_time": slot_time, "status": status}
        dead: set[WebSocket] = set()
        for ws in list(self._connections.get(doctor_service_id, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[doctor_service_id].discard(ws)


ws_manager = SlotConnectionManager()
