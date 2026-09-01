import asyncio
import json
import logging
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("ai_guard.websocket")


class ConnectionManager:
    """Manages active WebSocket connections for real-time notifications and telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast_json(self, message_type: str, data: dict):
        if not self.active_connections:
            return

        payload = json.dumps({"type": message_type, "data": data})
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    def sync_broadcast_alert(self, alert_dict: dict):
        """Synchronous helper for calling from background threads."""
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop_policy().get_event_loop()

            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_json("INTRUSION_ALERT", alert_dict),
                    loop
                )
        except Exception as e:
            logger.error(f"Failed to sync broadcast alert: {e}")


ws_manager = ConnectionManager()
