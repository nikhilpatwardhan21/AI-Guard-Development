import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import supervision as sv

logger = logging.getLogger("ai_guard.zone_monitor")


class ZoneMonitor:
    """Monitors restricted polygon zones and triggers intrusion detection events."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.name: str = "Restricted Zone"
        self.points: List[List[float]] = []
        self.is_normalized: bool = True
        self.is_active: bool = True
        self.color: str = "#EF4444"

        self.polygon_zone: Optional[sv.PolygonZone] = None
        self.current_pixel_polygon: Optional[np.ndarray] = None
        self.last_frame_dims: Optional[Tuple[int, int]] = None

        self._load_config()

    def _load_config(self):
        """Loads zone definition from JSON config file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.name = data.get("name", "Restricted Zone")
                    self.points = data.get("points", [[0.2, 0.25], [0.8, 0.25], [0.85, 0.85], [0.15, 0.85]])
                    self.is_normalized = data.get("is_normalized", True)
                    self.color = data.get("color", "#EF4444")
                    self.is_active = data.get("active", True)
                logger.info(f"Loaded zone configuration '{self.name}' with {len(self.points)} points.")
            except Exception as e:
                logger.error(f"Error loading zone config: {e}. Using fallback zone.")
                self._set_default_points()
        else:
            logger.info("Zone config file not found, creating default...")
            self._set_default_points()
            self.save_config()

    def _set_default_points(self):
        self.points = [[0.2, 0.25], [0.8, 0.25], [0.85, 0.85], [0.15, 0.85]]
        self.is_normalized = True
        self.is_active = True

    def save_config(self):
        """Saves current zone config to JSON file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "name": self.name,
                    "points": self.points,
                    "is_normalized": self.is_normalized,
                    "color": self.color,
                    "active": self.is_active
                }, f, indent=2)
            logger.info(f"Saved zone configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save zone config: {e}")

    def update_zone(self, points: List[List[float]], is_normalized: bool = True, name: Optional[str] = None, active: Optional[bool] = None):
        """Updates zone points and forces recalculation."""
        self.points = points
        self.is_normalized = is_normalized
        if name is not None:
            self.name = name
        if active is not None:
            self.is_active = active
        self.last_frame_dims = None  # Invalidate cached polygon zone
        self.save_config()

    def _get_pixel_points(self, width: int, height: int) -> np.ndarray:
        """Converts points into integer pixel polygon coordinates."""
        pts = []
        for pt in self.points:
            if self.is_normalized:
                px = int(pt[0] * width)
                py = int(pt[1] * height)
            else:
                px = int(pt[0])
                py = int(pt[1])
            pts.append([px, py])
        return np.array(pts, dtype=np.int32)

    def _ensure_polygon_zone(self, width: int, height: int):
        """Builds sv.PolygonZone if resolution changed or not initialized."""
        if self.polygon_zone is None or self.last_frame_dims != (width, height):
            pixel_pts = self._get_pixel_points(width, height)
            self.current_pixel_polygon = pixel_pts
            self.last_frame_dims = (width, height)

            # sv.Position.BOTTOM_CENTER checks feet/ground position for realistic zone intrusion
            self.polygon_zone = sv.PolygonZone(
                polygon=pixel_pts,
                triggering_anchors=[sv.Position.BOTTOM_CENTER]
            )

    def check_intrusion(self, detections: sv.Detections, frame_shape: Tuple[int, int]) -> Tuple[bool, np.ndarray, List[int]]:
        """
        Checks if any person detections are inside the restricted zone.
        Returns: (is_intruded, intruder_mask, intruding_tracker_ids)
        """
        if not self.is_active or len(self.points) < 3:
            return False, np.array([], dtype=bool), []

        height, width = frame_shape[:2]
        self._ensure_polygon_zone(width, height)

        if len(detections) == 0:
            return False, np.array([], dtype=bool), []

        # supervision PolygonZone trigger checks detections against polygon
        try:
            intruder_mask = self.polygon_zone.trigger(detections=detections)
            is_intruded = bool(np.any(intruder_mask))

            intruding_tracker_ids = []
            if is_intruded and detections.tracker_id is not None:
                for i, in_zone in enumerate(intruder_mask):
                    if in_zone and i < len(detections.tracker_id) and detections.tracker_id[i] is not None:
                        intruding_tracker_ids.append(int(detections.tracker_id[i]))

            return is_intruded, intruder_mask, intruding_tracker_ids
        except Exception as e:
            logger.error(f"Error checking intrusion: {e}")
            return False, np.array([False] * len(detections), dtype=bool), []

    def get_display_polygon(self, width: int, height: int) -> np.ndarray:
        """Returns integer pixel array suitable for cv2.polylines/fillPoly."""
        return self._get_pixel_points(width, height)
