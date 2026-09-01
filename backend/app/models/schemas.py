from typing import List, Optional
from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class ZoneConfig(BaseModel):
    name: str = "Restricted Zone"
    points: List[List[float]] = Field(
        default_factory=lambda: [
            [0.2, 0.3],
            [0.8, 0.3],
            [0.8, 0.85],
            [0.2, 0.85]
        ],
        description="Polygon vertices as normalized coordinates [0.0 - 1.0] or pixel coords [[x, y], ...]"
    )
    is_normalized: bool = True
    color: str = "#EF4444"  # Red
    active: bool = True


class IntrusionAlert(BaseModel):
    id: str
    timestamp: str
    zone_name: str
    intruder_count: int
    tracker_ids: List[int]
    screenshot_url: Optional[str] = None
    screenshot_path: Optional[str] = None


class SystemStatus(BaseModel):
    camera_active: bool
    detector_active: bool
    current_fps: float
    total_persons_detected: int
    zone_intruders_count: int
    active_tracker_ids: List[int]
    zone_active: bool
    email_alerts_enabled: bool
    system_time: str


class SettingsUpdate(BaseModel):
    confidence_threshold: Optional[float] = None
    alert_cooldown_seconds: Optional[int] = None
    camera_source: Optional[str] = None
    email_enabled: Optional[bool] = None
    alert_recipient: Optional[str] = None
