import cv2
import time
import json
import uuid
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
import numpy as np

from app.config import settings
from app.models.schemas import IntrusionAlert
from app.services.email_service import email_service

logger = logging.getLogger("ai_guard.alert_manager")


class AlertManager:
    """Handles intrusion alert throttling, screenshot capture, persistence, and notification dispatch."""

    def __init__(self):
        self.cooldown_seconds = settings.alert_cooldown_seconds
        self.screenshot_dir = Path(settings.screenshot_dir)
        self.log_file = Path(settings.log_dir) / "alerts_history.json"

        self.last_alert_time: float = 0.0
        self.tracker_alert_times: Dict[int, float] = {}  # {tracker_id: last_alert_time}
        self.alerts_history: List[IntrusionAlert] = []
        self.ws_broadcast_callback: Optional[Callable] = None
        self.lock = threading.Lock()

        self._init_storage()

    def _init_storage(self):
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    self.alerts_history = [IntrusionAlert(**item) for item in data]
                logger.info(f"Loaded {len(self.alerts_history)} past alert records.")
            except Exception as e:
                logger.error(f"Failed to load alert history log: {e}")
                self.alerts_history = []

    def set_broadcast_callback(self, callback: Callable):
        self.ws_broadcast_callback = callback

    def update_cooldown(self, cooldown_seconds: int):
        self.cooldown_seconds = max(5, cooldown_seconds)
        logger.info(f"Updated alert cooldown to {self.cooldown_seconds}s")

    def should_alert(self, intruding_ids: List[int]) -> bool:
        """Determines if a new alert should fire based on cooldown rules."""
        now = time.time()

        # Global cooldown check
        if (now - self.last_alert_time) < self.cooldown_seconds:
            return False

        # If we have tracked IDs, check if at least one ID is new or out of its personal cooldown
        if intruding_ids:
            unalerted_ids = [
                tid for tid in intruding_ids
                if (now - self.tracker_alert_times.get(tid, 0.0)) >= self.cooldown_seconds
            ]
            return len(unalerted_ids) > 0

        # Fallback if tracker IDs aren't available
        return (now - self.last_alert_time) >= self.cooldown_seconds

    def process_intrusion(
        self,
        annotated_frame: np.ndarray,
        zone_name: str,
        intruder_count: int,
        intruding_ids: List[int]
    ) -> Optional[IntrusionAlert]:
        """Triggers an alert if cooldown criteria are met."""
        if intruder_count <= 0 or not self.should_alert(intruding_ids):
            return None

        now = time.time()
        self.last_alert_time = now
        for tid in intruding_ids:
            self.tracker_alert_times[tid] = now

        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save screenshot
        screenshot_filename = f"{alert_id}.jpg"
        screenshot_path = str(self.screenshot_dir / screenshot_filename)
        screenshot_url = f"/api/alerts/{alert_id}/screenshot"

        try:
            cv2.imwrite(screenshot_path, annotated_frame)
            logger.info(f"Saved intrusion screenshot: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            screenshot_path = None
            screenshot_url = None

        alert = IntrusionAlert(
            id=alert_id,
            timestamp=timestamp_str,
            zone_name=zone_name,
            intruder_count=intruder_count,
            tracker_ids=intruding_ids,
            screenshot_url=screenshot_url,
            screenshot_path=screenshot_path
        )

        with self.lock:
            self.alerts_history.insert(0, alert)
            # Keep maximum 500 alerts in memory/log
            if len(self.alerts_history) > 500:
                self.alerts_history = self.alerts_history[:500]
            self._save_log_async()

        # Dispatch email asynchronously
        threading.Thread(
            target=email_service.send_alert_email,
            args=(alert_id, timestamp_str, zone_name, intruder_count, intruding_ids, screenshot_path),
            daemon=True,
            name=f"EmailDispatch-{alert_id}"
        ).start()

        # Broadcast via WebSocket if registered
        if self.ws_broadcast_callback:
            try:
                self.ws_broadcast_callback(alert.model_dump())
            except Exception as e:
                logger.error(f"Error in websocket alert broadcast: {e}")

        logger.warning(f"🚨 INTRUSION ALERT #{alert_id} TRIGGERED: {intruder_count} person(s) in {zone_name}!")
        return alert

    def _save_log_async(self):
        def _write():
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    json.dump([a.model_dump() for a in self.alerts_history], f, indent=2)
            except Exception as e:
                logger.error(f"Failed to persist alert history: {e}")

        threading.Thread(target=_write, daemon=True).start()

    def get_alerts(self, limit: int = 50) -> List[IntrusionAlert]:
        with self.lock:
            return self.alerts_history[:limit]

    def clear_alerts(self):
        with self.lock:
            self.alerts_history = []
            self._save_log_async()
        logger.info("Cleared alert history.")


alert_manager = AlertManager()
